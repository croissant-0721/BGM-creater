"""Multi-segment BGM generation + auto-stitching.

Each emotional cue gets its own Suno generation, then we stitch them together.
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import Config
from .gpt_analyzer import analyze_script_structured, normalize_tone
from .storyboard import analyze_storyboard
from .suno_client import SunoClient
from .tone_params import TONE_PARAMS, pick_bpm
from .quality import score_candidate
from .post import fade_and_normalize, crossfade_segments


# 叙事节点关键词列表 - 这些节点必须强制切cue
NARRATIVE_NODES = [
    "反转", "真相大白", "胜利", "和解", "结婚", "合作",
    "释然", "豁然开朗", "关键动作", "惊喜", "突变",
]


def _contains_narrative_node(text: str) -> bool:
    """检测文本中是否包含叙事节点关键词。"""
    if not text:
        return False
    return any(node in text for node in NARRATIVE_NODES)


def _compute_transition_type(prev_cue: dict, curr_cue: dict) -> str:
    """计算两个cue之间的过渡类型。

    Returns:
        "continue" - 相同tone，强度相似
        "gradual" - tone变化但相近（如紧张→动作）
        "abrupt" - 剧烈变化（如静默→爆发）
        "dramatic" - 叙事节点触发
    """
    if not prev_cue:
        return "cold"  # 第一个cue

    prev_tone = prev_cue.get("tone", "")
    curr_tone = curr_cue.get("tone", "")
    prev_intensity = prev_cue.get("intensity_peak", 5)
    curr_intensity = curr_cue.get("intensity_peak", 5)

    # 检查是否有叙事节点触发
    if curr_cue.get("has_narrative_node"):
        return "dramatic"

    # 检查是否是剧烈的情绪变化
    if _is_dramatic_change(prev_tone, curr_tone):
        return "abrupt"

    # 检查强度跳变
    if abs(curr_intensity - prev_intensity) >= 4:
        return "abrupt"

    # 相同tone
    if prev_tone == curr_tone:
        return "continue"

    # 默认为渐变
    return "gradual"


def detect_emotional_cues(
    analysis: dict,
    min_cue_duration: int = 6,
    max_cue_duration: int = 30,
) -> List[dict]:
    """从timeline或cues检测情绪分段。

    规则：
    - tone变化必须切
    - intensity跳变>=3必须切
    - 叙事节点（反转/真相/胜利等）必须切
    - 每段6-30秒
    - 相邻同tone段落会自动合并
    """
    if "cues" in analysis and analysis["cues"]:
        # 已经有cues（来自storyboard分析）
        cues = _split_long_cues(analysis["cues"], min_cue_duration, max_cue_duration)
        # 合并相邻的同情绪段落
        cues = _merge_same_tone_cues(cues)
        return cues

    # 从timeline构建cues
    timeline = analysis.get("timeline", [])
    if not timeline:
        return [{
            "id": 1,
            "start_s": 0,
            "end_s": analysis.get("total_duration", 60),
            "duration_s": analysis.get("total_duration", 60),
            "tone": analysis.get("primary_tone", "紧张"),
            "intensity_peak": analysis.get("primary_intensity", 5),
            "shot_ids": [],
        }]

    cues = []
    current_cue = {
        "start_s": 0,
        "tone": timeline[0].get("emotional_tone", "紧张"),
        "intensity_peak": timeline[0].get("intensity", 5),
    }

    for seg in timeline:
        duration = seg.get("duration", 0)
        seg_tone = normalize_tone(seg.get("emotional_tone", "紧张"))
        seg_intensity = seg.get("intensity", 5)

        # 检查是否包含叙事节点关键词
        seg_description = seg.get("scene_description", "")
        has_narrative_node = _contains_narrative_node(seg_description)

        # 检查是否需要切cue
        should_split = (
            has_narrative_node or  # 叙事节点强制切
            seg_tone != current_cue["tone"] or  # tone变化
            abs(seg_intensity - current_cue["intensity_peak"]) >= 3  # 强度跳变
        )

        if should_split:
            # 结束当前cue
            current_cue["end_s"] = current_cue["start_s"] + current_cue.get("duration_s", 0)
            current_cue["duration_s"] = current_cue["end_s"] - current_cue["start_s"]
            if current_cue["duration_s"] > 0:
                cues.append(current_cue)

            # 开始新cue
            current_cue = {
                "start_s": current_cue["end_s"],
                "tone": seg_tone,
                "intensity_peak": seg_intensity,
                "duration_s": duration,
            }
        else:
            # 继续当前cue
            current_cue["duration_s"] = current_cue.get("duration_s", 0) + duration
            # 更新强度峰值为最高
            current_cue["intensity_peak"] = max(current_cue["intensity_peak"], seg_intensity)

    # 添加最后一个cue
    if current_cue.get("duration_s", 0) > 0:
        current_cue["end_s"] = current_cue["start_s"] + current_cue["duration_s"]
        cues.append(current_cue)

    # 分配ID和shot_ids，并计算transition_from_previous
    for i, cue in enumerate(cues):
        cue["id"] = i + 1
        cue.setdefault("shot_ids", [])

        # 计算与前一个cue的过渡类型
        if i > 0:
            prev_cue = cues[i - 1]
            cue["transition_from_previous"] = _compute_transition_type(prev_cue, cue)
        else:
            cue["transition_from_previous"] = "cold"  # 第一个cue

    # 分割过长的cue，合并过短的
    cues = _split_long_cues(cues, min_cue_duration, max_cue_duration)

    # 确保完整覆盖
    _ensure_full_coverage(cues, analysis.get("total_duration", 60))

    return cues


def _split_long_cues(cues: List[dict], min_dur: int, max_dur: int) -> List[dict]:
    """分割过长的cue，合并过短的cue。"""
    if not cues:
        return cues

    result = []

    for cue in cues:
        duration = cue["end_s"] - cue["start_s"]

        if duration > max_dur:
            # 分割
            num_parts = (duration + max_dur - 1) // max_dur
            part_dur = duration // num_parts

            for i in range(num_parts):
                result.append({
                    "id": len(result) + 1,
                    "start_s": cue["start_s"] + i * part_dur,
                    "end_s": cue["start_s"] + (i + 1) * part_dur if i < num_parts - 1 else cue["end_s"],
                    "duration_s": part_dur if i < num_parts - 1 else cue["end_s"] - (cue["start_s"] + i * part_dur),
                    "tone": cue["tone"],
                    "intensity_peak": cue["intensity_peak"],
                    "shot_ids": [],
                })
        else:
            # 确保原始cue也有duration_s字段
            cue["duration_s"] = duration
            result.append(cue)

    # 合并过短的相邻cue（如果tone相同）
    merged = []
    i = 0
    while i < len(result):
        current = result[i]
        if current["duration_s"] < min_dur and i + 1 < len(result):
            next_cue = result[i + 1]
            if current["tone"] == next_cue["tone"]:
                # 合并
                merged.append({
                    "id": len(merged) + 1,
                    "start_s": current["start_s"],
                    "end_s": next_cue["end_s"],
                    "duration_s": next_cue["end_s"] - current["start_s"],
                    "tone": current["tone"],
                    "intensity_peak": max(current["intensity_peak"], next_cue["intensity_peak"]),
                    "shot_ids": [],
                })
                i += 2
                continue

        merged.append(current)
        i += 1

    return merged


def _merge_same_tone_cues(cues: List[dict]) -> List[dict]:
    """合并相邻的同情绪段落，减少不必要的分段。"""
    if not cues:
        return cues

    merged = []
    current = cues[0].copy()
    current["id"] = 1

    for next_cue in cues[1:]:
        # 如果tone相同，合并
        if current["tone"] == next_cue["tone"]:
            current["end_s"] = next_cue["end_s"]
            current["duration_s"] = current["end_s"] - current["start_s"]
            current["intensity_peak"] = max(current["intensity_peak"], next_cue.get("intensity_peak", 5))
            current["shot_ids"] = list(set(current.get("shot_ids", []) + next_cue.get("shot_ids", [])))
        else:
            # tone不同，保存当前，开始新的
            merged.append(current)
            current = next_cue.copy()
            current["id"] = len(merged) + 1

    merged.append(current)
    return merged


def _ensure_full_coverage(cues: List[dict], total_duration: int) -> None:
    """确保cues完整覆盖整个时长。"""
    if not cues:
        cues.append({
            "id": 1,
            "start_s": 0,
            "end_s": total_duration,
            "duration_s": total_duration,
            "tone": "紧张",
            "intensity_peak": 5,
            "shot_ids": [],
        })
        return

    # 确保从0开始
    if cues[0]["start_s"] != 0:
        cues[0]["start_s"] = 0
        cues[0]["duration_s"] = cues[0]["end_s"] - 0

    # 确保到total结束
    if cues[-1]["end_s"] != total_duration:
        cues[-1]["end_s"] = total_duration
        cues[-1]["duration_s"] = total_duration - cues[-1]["start_s"]


def build_prompt_for_cue(cue: dict, title: str) -> dict:
    """为单个cue构建Suno prompt。"""
    tone = cue["tone"]
    intensity = cue["intensity_peak"]
    duration = cue["duration_s"]

    params = TONE_PARAMS.get(tone, TONE_PARAMS["紧张"])
    bpm = pick_bpm(tone, intensity)
    key = params.key_options[0]

    # 构建prompt
    prompt = (
        f"*** INSTRUMENTAL ONLY - NO VOCALS ***\n"
        f"Create a {duration}s {params.name_en} cinematic background music.\n"
        f"BPM: {bpm}, Key: {key}\n"
        f"Instruments: {', '.join(params.instrumentation[:3])}\n"
        f"Style: {params.production_style}\n\n"
        f"CRITICAL: NO singing, NO lyrics, NO vocal samples, NO choir.\n"
        f"Pure orchestral/instrumental only."
    )

    tags = f"{params.tags_seed}, {bpm}bpm, {key}, cinematic, instrumental"

    return {
        "cue_id": cue["id"],
        "duration_s": duration,
        "prompt": prompt,
        "tags": tags[:120],
        "tone": tone,
        "intensity": intensity,
    }


def generate_segment(
    cue: dict,
    title: str,
    output_dir: Path,
    cfg: Config,
) -> dict:
    """为单个cue生成音频段。"""
    prompt_data = build_prompt_for_cue(cue, title)

    payload = {
        "prompt": prompt_data["prompt"],
        "tags": prompt_data["tags"],
        "title": f"{title}_cue{cue['id']}",
        "mv": "chirp-v4",
        "make_instrumental": True,
    }

    client = SunoClient(cfg)
    candidates = client.generate(payload)

    # 选择最佳候选
    target_bpm = pick_brompt(cue["tone"], cue["intensity_peak"])
    scored = [score_candidate(p, target_bpm) for p in candidates]
    scored.sort(key=lambda m: m["score"], reverse=True)
    best = Path(scored[0]["path"])

    # 裁剪到精确时长
    output_file = output_dir / f"cue_{cue['id']}_{cue['tone']}.mp3"
    fade_and_normalize(
        best,
        target_duration_s=cue["duration_s"],
        target_lufs=cfg.target_lufs,
        fade_out_ms=0,  # 不fade，让stitcher处理
        out_path=output_file,
    )

    return {
        "cue_id": cue["id"],
        "audio": str(output_file),
        "duration_s": cue["duration_s"],
        "tone": cue["tone"],
    }


def stitch_segments(
    segments: List[dict],
    cues: List[dict],
    output_path: Path,
) -> Path:
    """拼接所有音频段为完整BGM。

    transition策略（基于transition_from_previous字段）：
    - "continue"（相同情绪）: crossfade 800ms
    - "gradual"（中等变化）: crossfade 1200ms
    - "abrupt" / "dramatic"（剧烈变化）: hard cut (0ms)
    - "cold"（第一个）: 无过渡
    """
    if not segments:
        return output_path

    if len(segments) == 1:
        # 只有一段，直接返回
        from pathlib import Path
        import shutil
        shutil.copy(segments[0]["audio"], output_path)
        return output_path

    # 计算transition类型
    from pydub import AudioSegment

    segment_paths = [s["audio"] for s in segments]
    crossfade_durations = []

    for i in range(1, len(cues)):  # 从第二个开始（索引1对应segments索引1）
        transition_type = cues[i].get("transition_from_previous", "gradual")

        # 根据transition类型决定crossfade时长
        if transition_type == "continue":
            crossfade_durations.append(800)
        elif transition_type in ("abrupt", "dramatic", "cold"):
            crossfade_durations.append(0)  # hard cut
        else:  # "gradual" 或其他
            crossfade_durations.append(1200)

    # 依次拼接
    result = AudioSegment.from_mp3(segment_paths[0])

    for i in range(1, len(segment_paths)):
        next_seg = AudioSegment.from_mp3(segment_paths[i])
        cf_duration = crossfade_durations[i - 1]

        if cf_duration > 0:
            result = result.append(next_seg, crossfade=cf_duration)
        else:
            # hard cut
            result = result + next_seg

    # 整体fade out
    result = result.fade_out(3000)

    # 导出
    result.export(str(output_path), format="mp3", bitrate="192k")
    return output_path


def _is_dramatic_change(tone1: str, tone2: str) -> bool:
    """判断是否是剧烈的情绪变化。"""
    dramatic_pairs = [
        ("静默", "动作"),
        ("静默", "反击"),
        ("静默", "恐惧"),
        ("温馨", "恐惧"),
        ("温馨", "紧张"),
        ("悲伤", "励志"),
        ("悲伤", "动作"),
        ("豪门", "恐惧"),
        ("豪门", "异常"),
    ]

    return (tone1, tone2) in dramatic_pairs or (tone2, tone1) in dramatic_pairs


def generate_bgm_multisegment(
    analysis: dict,
    title: str,
    out_dir: Path,
    *,
    config: Optional[Config] = None,
) -> dict:
    """多段生成+拼接的完整pipeline。

    优化：相同情绪只生成一段BGM，然后重复使用。
    """
    cfg = config or Config()
    cfg.ensure_dirs()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 检测emotional cues（已合并相邻同情绪）
    cues = detect_emotional_cues(analysis)

    # 2. 按情绪分组，每种情绪只生成一段BGM
    segments_dir = out_dir / "segments"
    segments_dir.mkdir(exist_ok=True)

    # 记录已生成的情绪（tone -> segment info）
    generated_tones = {}
    segments = []

    for cue in cues:
        tone = cue["tone"]
        if tone not in generated_tones:
            # 为这个情绪生成新的BGM段
            print(f"[multisegment] Generating NEW {tone} segment for cue {cue['id']}: {cue['start_s']}-{cue['end_s']}s", flush=True)

            # ⚠️ 在生成新段之前等待，避免API速率限制
            if generated_tones:
                wait_time = 30  # 第一次之后等待30秒
                print(f"[multisegment] Waiting {wait_time}s before next generation to avoid rate limit...", flush=True)
                time.sleep(wait_time)

            try:
                segment = generate_segment(cue, title, segments_dir, cfg)
                generated_tones[tone] = segment
                print(f"[multisegment] SUCCESS: {tone} segment generated: {segment['audio']}", flush=True)
            except Exception as e:
                print(f"[multisegment] FAILED to generate {tone} segment: {e}", flush=True)
                # 回退策略：使用已生成的最接近的tone
                if generated_tones:
                    fallback_tone = list(generated_tones.keys())[0]
                    print(f"[multisegment] Falling back to {fallback_tone} segment", flush=True)
                    segment = generated_tones[fallback_tone].copy()
                else:
                    raise
        else:
            # 复用已生成的同情绪BGM
            segment = generated_tones[tone].copy()
            print(f"[multisegment] Reusing {tone} segment for cue {cue['id']}: {cue['start_s']}-{cue['end_s']}s", flush=True)

        segments.append(segment)

    # 3. 拼接所有段
    print(f"[multisegment] Stitching {len(segments)} segments...", flush=True)
    print(f"[multisegment] Generated {len(generated_tones)} unique segments: {list(generated_tones.keys())}", flush=True)
    # 统一输出命名为 episode_final.mp3
    final_path = out_dir / "episode_final.mp3"

    stitch_segments(segments, cues, final_path)

    return {
        "pipeline": "multisegment",
        "total_duration_s": sum(s["duration_s"] for s in segments),
        "segments": [
            {
                "cue_id": s["cue_id"],
                "start_s": cues[i]["start_s"],
                "end_s": cues[i]["end_s"],
                "audio": s["audio"],
                "tone": cues[i].get("tone", ""),
            }
            for i, s in enumerate(segments)
        ],
        "final_audio": str(final_path),
        "cues": cues,
        "unique_segments": len(generated_tones),
        "unique_tones": list(generated_tones.keys()),
    }


# 辅助函数
def pick_brompt(tone: str, intensity: int) -> int:
    """别名，避免与pick_bpm冲突。"""
    return pick_bpm(tone, intensity)
