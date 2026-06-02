"""Multi-segment BGM generation + auto-stitching.

每个情绪段(cue)都精确对应一段 BGM；同情绪只调一次 Suno，但每个 cue 都按
自己的时长独立裁剪，保证拼出来的总时长 == 剧本总时长，绝不超、不错位。
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import List, Optional, Dict

from pydub import AudioSegment

from .config import Config
from .gpt_analyzer import normalize_tone
from .suno_client import SunoClient
from .tone_params import TONE_PARAMS, pick_bpm
from .quality import score_candidate
from .post import _loudness_normalize
from .stinger import plan_stingers, apply_stingers


# 叙事节点关键词列表 - 这些节点必须强制切cue
NARRATIVE_NODES = [
    "反转", "真相大白", "胜利", "和解", "结婚", "合作",
    "释然", "豁然开朗", "关键动作", "惊喜", "突变",
]

# transition 类型 → crossfade 时长(ms)
# 注意：除第一段(cold)外一律给真实 crossfade，不再用 0ms 硬切（硬切把两段
# 调性/速度/配器都不同的音乐直接对接，听感非常生硬）。反差越大 crossfade 越短，
# 仍保留情绪对比，但不会"啪"地一下。
TRANSITION_CROSSFADE_MS = {
    "continue": 1200,   # 同情绪：最平滑
    "gradual": 1000,    # 中等变化
    "abrupt": 800,      # 剧烈变化：短一些但仍交叠
    "dramatic": 700,    # 叙事爽点：最短，保留冲击感但不突兀
    "cold": 0,          # 第一段：无前序，无过渡
}


def _contains_narrative_node(text: str) -> bool:
    """检测文本中是否包含叙事节点关键词。"""
    if not text:
        return False
    return any(node in text for node in NARRATIVE_NODES)


def _is_dramatic_change(tone1: str, tone2: str) -> bool:
    """判断是否是剧烈的情绪变化。"""
    dramatic_pairs = [
        ("静默", "动作"), ("静默", "反击"), ("静默", "恐惧"),
        ("温馨", "恐惧"), ("温馨", "紧张"),
        ("悲伤", "励志"), ("悲伤", "动作"),
        ("豪门", "恐惧"), ("豪门", "异常"),
    ]
    return (tone1, tone2) in dramatic_pairs or (tone2, tone1) in dramatic_pairs


def _compute_transition_type(prev_cue: Optional[dict], curr_cue: dict) -> str:
    """计算两个cue之间的过渡类型。"""
    if not prev_cue:
        return "cold"

    prev_tone = prev_cue.get("tone", "")
    curr_tone = curr_cue.get("tone", "")
    prev_intensity = prev_cue.get("intensity_peak", 5)
    curr_intensity = curr_cue.get("intensity_peak", 5)

    if curr_cue.get("has_narrative_node"):
        return "dramatic"
    if _is_dramatic_change(prev_tone, curr_tone):
        return "abrupt"
    if abs(curr_intensity - prev_intensity) >= 4:
        return "abrupt"
    if prev_tone == curr_tone:
        return "continue"
    return "gradual"


def _crossfade_for(transition: str) -> int:
    """根据过渡类型返回 crossfade 时长(ms)。"""
    return TRANSITION_CROSSFADE_MS.get(transition, 1200)


# ----------------------------------------------------------------------------
# cue 检测
# ----------------------------------------------------------------------------

def detect_emotional_cues(
    analysis: dict,
    min_cue_duration: int = 6,
    max_cue_duration: int = 30,
) -> List[dict]:
    """从timeline或cues检测情绪分段。

    无论输入来自 storyboard(cues) 还是 timeline，最终都会：
    - 平铺成连续、无空隙、无重叠的段
    - 各段时长之和 == 剧本总时长（保证后续 BGM 不超时、不错位）
    - 计算每段相对上一段的 transition_from_previous
    """
    total = analysis.get("total_duration_s") or analysis.get("total_duration") or 0

    if analysis.get("cues"):
        # 来自 storyboard 的 cue 列表
        raw = _split_long_cues(_coerce_cues(analysis["cues"]), min_cue_duration, max_cue_duration)
        raw = _merge_same_tone_cues(raw)
    elif analysis.get("timeline"):
        raw = _build_cues_from_timeline(analysis, min_cue_duration, max_cue_duration)
    else:
        raw = [{
            "start_s": 0,
            "end_s": total or 60,
            "duration_s": total or 60,
            "tone": normalize_tone(analysis.get("primary_tone", "紧张")),
            "intensity_peak": analysis.get("primary_intensity", 5),
        }]

    if not total:
        total = sum(
            c.get("duration_s") or (c.get("end_s", 0) - c.get("start_s", 0)) for c in raw
        ) or 60

    cues = _normalize_cue_timeline(raw, int(total))
    _assign_transitions(cues)
    return cues


def _coerce_cues(cues: List[dict]) -> List[dict]:
    """把外部 cue 列表统一成带 start_s/end_s/duration_s/tone/intensity_peak 的形式。"""
    out = []
    for c in cues:
        start = c.get("start_s", 0)
        end = c.get("end_s", start + c.get("duration_s", 0))
        nc = dict(c)
        nc["start_s"] = start
        nc["end_s"] = end
        nc["duration_s"] = max(0, end - start)
        nc["tone"] = normalize_tone(c.get("tone", "紧张"))
        nc.setdefault("intensity_peak", c.get("intensity", 5))
        out.append(nc)
    return out


def _build_cues_from_timeline(analysis: dict, min_dur: int, max_dur: int) -> List[dict]:
    """从带时间戳的 timeline 构建情绪段。"""
    timeline = analysis["timeline"]
    first_tone = normalize_tone(timeline[0].get("emotional_tone", "紧张"))
    current = {
        "start_s": 0,
        "tone": first_tone,
        "intensity_peak": timeline[0].get("intensity", 5),
        "duration_s": 0,
    }

    cues: List[dict] = []
    for seg in timeline:
        duration = seg.get("duration", 0)
        seg_tone = normalize_tone(seg.get("emotional_tone", "紧张"))
        seg_intensity = seg.get("intensity", 5)
        has_node = _contains_narrative_node(seg.get("scene_description", ""))

        should_split = (
            has_node
            or seg_tone != current["tone"]
            or abs(seg_intensity - current["intensity_peak"]) >= 3
        )

        if should_split and current["duration_s"] > 0:
            current["end_s"] = current["start_s"] + current["duration_s"]
            cues.append(current)
            current = {
                "start_s": current["end_s"],
                "tone": seg_tone,
                "intensity_peak": seg_intensity,
                "duration_s": duration,
            }
        else:
            current["duration_s"] += duration
            current["intensity_peak"] = max(current["intensity_peak"], seg_intensity)

    if current["duration_s"] > 0:
        current["end_s"] = current["start_s"] + current["duration_s"]
        cues.append(current)

    return _split_long_cues(cues, min_dur, max_dur)


def _split_long_cues(cues: List[dict], min_dur: int, max_dur: int) -> List[dict]:
    """分割过长的cue，合并过短的相邻同情绪cue。"""
    if not cues:
        return cues

    result: List[dict] = []
    for cue in cues:
        start = cue.get("start_s", 0)
        end = cue.get("end_s", start + cue.get("duration_s", 0))
        duration = end - start

        if duration > max_dur:
            num_parts = (duration + max_dur - 1) // max_dur
            part_dur = duration // num_parts
            for i in range(num_parts):
                p_start = start + i * part_dur
                p_end = end if i == num_parts - 1 else start + (i + 1) * part_dur
                result.append({
                    "start_s": p_start,
                    "end_s": p_end,
                    "duration_s": p_end - p_start,
                    "tone": cue["tone"],
                    "intensity_peak": cue.get("intensity_peak", 5),
                })
        else:
            cue["duration_s"] = duration
            result.append(cue)

    # 合并过短的相邻同情绪cue
    merged: List[dict] = []
    i = 0
    while i < len(result):
        current = result[i]
        if current["duration_s"] < min_dur and i + 1 < len(result) \
                and current["tone"] == result[i + 1]["tone"]:
            nxt = result[i + 1]
            merged.append({
                "start_s": current["start_s"],
                "end_s": nxt["end_s"],
                "duration_s": nxt["end_s"] - current["start_s"],
                "tone": current["tone"],
                "intensity_peak": max(current.get("intensity_peak", 5), nxt.get("intensity_peak", 5)),
            })
            i += 2
            continue
        merged.append(current)
        i += 1

    return merged


def _merge_same_tone_cues(cues: List[dict], intensity_tol: int = 3) -> List[dict]:
    """合并相邻的同情绪段落 —— 但强度跳变 >= intensity_tol 时不合并，
    保留剧情起伏节拍（否则一段平铺紧张会抹平高潮，导致"卡不上点"）。"""
    if not cues:
        return cues

    merged = [dict(cues[0])]
    for nxt in cues[1:]:
        cur = merged[-1]
        same_tone = cur["tone"] == nxt["tone"]
        close = abs(cur.get("intensity_peak", 5) - nxt.get("intensity_peak", 5)) < intensity_tol
        if same_tone and close:
            cur["end_s"] = nxt["end_s"]
            cur["duration_s"] = cur["end_s"] - cur["start_s"]
            cur["intensity_peak"] = max(cur.get("intensity_peak", 5), nxt.get("intensity_peak", 5))
        else:
            merged.append(dict(nxt))
    return merged


def _normalize_cue_timeline(cues: List[dict], total: int) -> List[dict]:
    """把cue平铺成连续、无空隙、总和==total的时间线。

    - 从 0 开始，逐段首尾相接
    - 累计超过 total 的段被截断，其后丢弃 → 永不超时
    - 若总长不足 total，最后一段拉长补齐 → 完整覆盖
    """
    if total <= 0:
        total = sum(c.get("duration_s", 0) for c in cues) or 60

    out: List[dict] = []
    cursor = 0
    for c in cues:
        if cursor >= total:
            break
        dur = c.get("duration_s") or (c.get("end_s", 0) - c.get("start_s", 0))
        if dur <= 0:
            continue
        start = cursor
        end = min(total, cursor + dur)
        nc = dict(c)
        nc["start_s"] = start
        nc["end_s"] = end
        nc["duration_s"] = end - start
        out.append(nc)
        cursor = end

    if not out:
        out = [{
            "start_s": 0, "end_s": total, "duration_s": total,
            "tone": "紧张", "intensity_peak": 5,
        }]

    # 不足总时长 → 最后一段补齐
    if out[-1]["end_s"] < total:
        out[-1]["end_s"] = total
        out[-1]["duration_s"] = total - out[-1]["start_s"]

    for i, c in enumerate(out):
        c["id"] = i + 1
        c["tone"] = normalize_tone(c.get("tone", "紧张"))
        c.setdefault("intensity_peak", c.get("intensity", 5))
        c.setdefault("shot_ids", [])
    return out


def _assign_transitions(cues: List[dict]) -> None:
    """为每个cue计算 transition_from_previous。"""
    for i, cue in enumerate(cues):
        cue["transition_from_previous"] = _compute_transition_type(
            cues[i - 1] if i > 0 else None, cue
        )


# ----------------------------------------------------------------------------
# prompt + 生成
# ----------------------------------------------------------------------------

def build_prompt_for_cue(cue: dict, title: str) -> dict:
    """为单个cue构建Suno prompt。"""
    tone = cue["tone"]
    intensity = cue["intensity_peak"]
    duration = cue["duration_s"]

    params = TONE_PARAMS.get(tone, TONE_PARAMS["紧张"])
    bpm = pick_bpm(tone, intensity)
    key = params.key_options[0]

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


def _generate_raw_for_tone(cue: dict, title: str, cfg: Config) -> Path:
    """为某种情绪调用一次 Suno，返回打分最高的**原始候选**(未裁剪)。"""
    prompt_data = build_prompt_for_cue(cue, title)
    payload = {
        "prompt": prompt_data["prompt"],
        "tags": prompt_data["tags"],
        "title": f"{title}_{cue['tone']}",
        "mv": cfg.suno_model,
        "make_instrumental": True,
    }

    client = SunoClient(cfg)
    candidates = client.generate(payload)

    target_bpm = pick_bpm(cue["tone"], cue["intensity_peak"])
    scored = [score_candidate(p, target_bpm) for p in candidates]
    scored.sort(key=lambda m: m["score"], reverse=True)
    best = scored[0]
    print(f"[multisegment] {cue['tone']} 选中候选 score={best['score']} "
          f"vocal={best['vocal_energy_ratio']} bpm={best['bpm_detected']}/{target_bpm}", flush=True)
    return Path(best["path"])


def _render_cue_clip(raw_path: Path, length_ms: int) -> AudioSegment:
    """从原始候选裁出精确长度的片段；不足则补静音(strict)。"""
    audio = AudioSegment.from_mp3(str(raw_path))
    if len(audio) >= length_ms:
        return audio[:length_ms]
    pad = AudioSegment.silent(duration=length_ms - len(audio), frame_rate=audio.frame_rate)
    return audio + pad


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------

def generate_bgm_multisegment(
    analysis: dict,
    title: str,
    out_dir: Path,
    *,
    config: Optional[Config] = None,
    use_stinger: bool = True,
    parallel: bool = True,
    submit_stagger_s: float = 3.0,
) -> dict:
    """多段生成 + 拼接的完整 pipeline。

    - 每种情绪只调一次 Suno（省成本），保存原始候选
    - 每个 cue 从所属情绪的原始候选按**自己的精确时长**单独裁剪
    - 拼接时按过渡类型 crossfade，并补偿重叠量，使总长 == 剧本总时长
    - use_stinger=True 时在剧情高潮/反转的精确时间点叠加 stinger 重音（卡点）
    - parallel=True 时并发提交+轮询所有情绪（错开 submit_stagger_s 秒防突发限流），
      总耗时≈最慢一段而非相加；False 时串行（每段间等 30s）
    """
    cfg = config or Config()
    cfg.ensure_dirs()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 检测 cues（已平铺、总和==总时长、带 transition）
    cues = detect_emotional_cues(analysis)
    total_duration = cues[-1]["end_s"]

    print(f"[multisegment] 共 {len(cues)} 段, 总时长 {total_duration}s:", flush=True)
    for c in cues:
        print(f"  cue{c['id']}: {c['start_s']}-{c['end_s']}s ({c['duration_s']}s) "
              f"| {c['tone']} | 强度{c['intensity_peak']} | {c['transition_from_previous']}", flush=True)

    # 2. 每种情绪生成一次原始候选（每种情绪取第一个出现的 cue 作 prompt 依据）
    unique_tones: List[str] = []
    cue_for_tone: Dict[str, dict] = {}
    for cue in cues:
        if cue["tone"] not in cue_for_tone:
            cue_for_tone[cue["tone"]] = cue
            unique_tones.append(cue["tone"])

    raw_by_tone: Dict[str, Path] = {}
    if parallel and len(unique_tones) > 1:
        # 并发：错开提交防突发限流，再并行轮询（各段服务器端同时生成）
        from concurrent.futures import ThreadPoolExecutor

        def _gen(item):
            idx, tone = item
            if idx > 0:
                time.sleep(idx * submit_stagger_s)  # 错开提交
            try:
                return tone, _generate_raw_for_tone(cue_for_tone[tone], title, cfg)
            except Exception as e:
                print(f"[multisegment] {tone} 生成失败: {e}", flush=True)
                return tone, None

        print(f"[multisegment] 并行生成 {len(unique_tones)} 种情绪 {unique_tones} "
              f"(错开 {submit_stagger_s}s 提交)...", flush=True)
        results: Dict[str, Optional[Path]] = {}
        with ThreadPoolExecutor(max_workers=min(len(unique_tones), 6)) as ex:
            for tone, raw in ex.map(_gen, list(enumerate(unique_tones))):
                results[tone] = raw

        ok_tones = [t for t in unique_tones if results.get(t)]
        if not ok_tones:
            raise RuntimeError("所有情绪段生成均失败")
        for tone in unique_tones:
            if results.get(tone):
                raw_by_tone[tone] = results[tone]
            else:
                print(f"[multisegment] {tone} 回退到 {ok_tones[0]} 段", flush=True)
                raw_by_tone[tone] = results[ok_tones[0]]
    else:
        # 串行：每段之间等 30s 避免限流
        for i, tone in enumerate(unique_tones):
            if i > 0:
                print(f"[multisegment] 等待 30s 避免限流...", flush=True)
                time.sleep(30)
            print(f"[multisegment] 生成新情绪段: {tone}", flush=True)
            try:
                raw_by_tone[tone] = _generate_raw_for_tone(cue_for_tone[tone], title, cfg)
            except Exception as e:
                print(f"[multisegment] {tone} 生成失败: {e}", flush=True)
                if raw_by_tone:
                    fallback = next(iter(raw_by_tone))
                    print(f"[multisegment] 回退到已生成的 {fallback} 段", flush=True)
                    raw_by_tone[tone] = raw_by_tone[fallback]
                else:
                    raise

    # 3. 为每个 cue 渲染精确时长的片段（同情绪也各自独立裁剪）
    segments_dir = out_dir / "segments"
    segments_dir.mkdir(exist_ok=True)

    clips: List[AudioSegment] = []
    seg_meta: List[dict] = []
    for cue in cues:
        cf_in = _crossfade_for(cue["transition_from_previous"]) if cue["id"] > 1 else 0
        # 多裁 cf_in 的长度，拼接 crossfade 重叠后净长 == cue 时长
        length_ms = cue["duration_s"] * 1000 + cf_in
        clip = _render_cue_clip(raw_by_tone[cue["tone"]], length_ms)
        clips.append(clip)

        seg_path = segments_dir / f"cue_{cue['id']}_{cue['tone']}.mp3"
        clip.export(str(seg_path), format="mp3", bitrate="192k")
        seg_meta.append({
            "cue_id": cue["id"],
            "start_s": cue["start_s"],
            "end_s": cue["end_s"],
            "duration_s": cue["duration_s"],
            "tone": cue["tone"],
            "transition": cue["transition_from_previous"],
            "audio": str(seg_path),
        })

    # 4. 卡点 stinger 规划（从细粒度 analysis 取剧情高潮/反转点）
    stinger_plan = plan_stingers(analysis, total_duration) if use_stinger else []
    if stinger_plan:
        impacts = [p["ts_ms"] // 1000 for p in stinger_plan if p["kind"] == "impact"]
        print(f"[multisegment] 卡点 stinger {len(impacts)} 处 @ {impacts}s", flush=True)

    # 5. 拼接（crossfade 补偿后总长 == 各 cue 时长之和） + 叠加 stinger
    final_path = out_dir / "episode_final.mp3"
    _stitch(clips, cues, total_duration, final_path, cfg, stinger_plan=stinger_plan)

    return {
        "pipeline": "multisegment",
        "total_duration_s": total_duration,
        "segments": seg_meta,
        "final_audio": str(final_path),
        "cues": cues,
        "unique_segments": len(raw_by_tone),
        "unique_tones": list(raw_by_tone.keys()),
        "stingers": stinger_plan,
    }


def _stitch(
    clips: List[AudioSegment],
    cues: List[dict],
    total_duration: int,
    output_path: Path,
    cfg: Config,
    stinger_plan: Optional[List[dict]] = None,
) -> Path:
    """拼接所有片段，硬卡死到总时长，叠加 stinger，整体淡出，再统一响度归一。

    片段 i (i>=1) 已多裁 cf_in 长度，crossfade 重叠 cf_in 后净增长 == cue 时长，
    因此拼完总长 == sum(cue.duration_s) == total_duration。
    """
    if not clips:
        return output_path

    result = clips[0]
    for i in range(1, len(clips)):
        cf = _crossfade_for(cues[i]["transition_from_previous"])
        if cf > 0:
            cf = min(cf, len(result) - 1, len(clips[i]) - 1)
            result = result.append(clips[i], crossfade=max(0, cf))
        else:
            result = result + clips[i]

    # 硬卡死到精确总时长：超出截断、不足补静音
    target_ms = total_duration * 1000
    if len(result) > target_ms:
        result = result[:target_ms]
    elif len(result) < target_ms:
        result = result + AudioSegment.silent(
            duration=target_ms - len(result), frame_rate=result.frame_rate
        )

    # 卡点 stinger 叠加（在淡出/归一之前，纳入整体响度控制，避免削顶）
    if stinger_plan:
        result = apply_stingers(result, stinger_plan)

    # 整体淡出
    result = result.fade_out(min(cfg.fade_out_ms, len(result)))

    result.export(str(output_path), format="mp3", bitrate="192k")
    # 统一响度归一到 -18 LUFS（对整曲做一次，保证段间响度一致）
    _loudness_normalize(output_path, cfg.target_lufs)
    return output_path
