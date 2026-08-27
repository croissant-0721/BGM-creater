"""Automatic emotion segmentation for scripts with dramatic arcs."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from .config import Config
from .gpt_analyzer import analyze_script_structured
from .suno_client import SunoClient
from .tone_params import TONE_PARAMS, pick_bpm
from .post import fade_and_normalize, crossfade_segments
from .quality import score_candidate


@dataclass
class Segment:
    """A musical segment with consistent emotional tone."""
    tone: str
    start_s: int
    end_s: int
    duration: int
    intensity: int
    description: str


def detect_emotional_segments(analysis: dict) -> List[Segment]:
    """Analyze timeline and detect when emotional tone shifts significantly.

    Rules:
    1. Group consecutive scenes with same tone class
    2. Split when tone class changes (TENSE → WARM or WARM → TENSE)
    3. Only split if the new segment is >5 seconds
    """
    timeline = analysis.get("timeline", [])
    if not timeline:
        # No timeline data, single segment
        return [Segment(
            tone=analysis["primary_tone"],
            start_s=0,
            end_s=analysis.get("total_duration", 80),
            duration=analysis.get("total_duration", 80),
            intensity=analysis["primary_intensity"],
            description="Full scene (no timeline data)"
        )]

    total_duration = analysis.get("total_duration", sum(s.get("duration", 0) for s in timeline))

    # 定义情绪类别
    TENSE_TONES = {"紧张", "恐惧", "羞辱", "静默", "动作", "反击", "愤怒", "惊险"}
    WARM_TONES = {"温馨", "励志", "豪门", "释然", "惊喜", "暧昧", "胜利"}
    NEUTRAL_TONES = {"悬疑", "异常", "惊"}

    def get_tone_class(tone: str) -> str:
        if tone in TENSE_TONES:
            return "TENSE"
        elif tone in WARM_TONES:
            return "WARM"
        else:
            return "NEUTRAL"

    # 按情绪类别分组扫描
    segments = []
    current_start = 0
    current_tone_class = None
    current_scenes = []

    for scene in timeline:
        tone = scene.get("emotional_tone", analysis["primary_tone"])
        tone_class = get_tone_class(tone)
        duration = scene.get("duration", 0)

        # 初始化
        if current_tone_class is None:
            current_tone_class = tone_class
            current_scenes = [scene]
            current_start = 0
            continue

        # 检查是否需要开始新段
        if tone_class != current_tone_class:
            # 情绪类别变化，结束当前段
            seg_duration = sum(s.get("duration", 0) for s in current_scenes)
            if seg_duration > 0:
                # 使用该段的主导情绪
                tone_counts = {}
                for s in current_scenes:
                    t = s.get("emotional_tone", analysis["primary_tone"])
                    tone_counts[t] = tone_counts.get(t, 0) + 1
                dominant_tone = max(tone_counts.items(), key=lambda x: x[1])[0]

                segments.append(Segment(
                    tone=dominant_tone,
                    start_s=current_start,
                    end_s=current_start + seg_duration,
                    duration=seg_duration,
                    intensity=int(sum(s.get("intensity", 5) for s in current_scenes) / len(current_scenes)),
                    description=f"{current_tone_class} segment"
                ))

            # 开始新段
            current_start += seg_duration
            current_tone_class = tone_class
            current_scenes = [scene]
        else:
            current_scenes.append(scene)

    # 添加最后一段
    if current_scenes:
        seg_duration = sum(s.get("duration", 0) for s in current_scenes)
        if seg_duration > 0:
            tone_counts = {}
            for s in current_scenes:
                t = s.get("emotional_tone", analysis["primary_tone"])
                tone_counts[t] = tone_counts.get(t, 0) + 1
            dominant_tone = max(tone_counts.items(), key=lambda x: x[1])[0]

            segments.append(Segment(
                tone=dominant_tone,
                start_s=current_start,
                end_s=current_start + seg_duration,
                duration=seg_duration,
                intensity=int(sum(s.get("intensity", 5) for s in current_scenes) / len(current_scenes)),
                description=f"{current_tone_class} segment"
            ))

    # 合并太短的段（<5秒）到相邻段
    if len(segments) > 1:
        merged = []
        for i, seg in enumerate(segments):
            if seg.duration < 5:
                # 合并到前一段或后一段
                if i == 0:
                    # 合并到后一段
                    segments[i + 1].tone = seg.tone
                    segments[i + 1].start_s = seg.start_s
                    segments[i + 1].duration += seg.duration
                elif i == len(segments) - 1:
                    # 合并到前一段
                    merged[-1].duration += seg.duration
                else:
                    # 合并到较长的那一段
                    if merged[-1].duration >= segments[i + 1].duration:
                        merged[-1].duration += seg.duration
                    else:
                        segments[i + 1].start_s = seg.start_s
                        segments[i + 1].duration += seg.duration
            else:
                merged.append(seg)
        segments = merged

    # 如果最终只有一段或没有有效分段，返回单段
    if len(segments) <= 1:
        return [Segment(
            tone=analysis["primary_tone"],
            start_s=0,
            end_s=total_duration,
            duration=total_duration,
            intensity=analysis["primary_intensity"],
            description="Single emotional arc"
        )]

    return segments


def generate_segmented_bgm(
    script_text: str,
    title: str,
    out_dir: Path,
    *,
    config: Optional[Config] = None,
    use_auto_segments: bool = True,
    force_single_segment: bool = False,
) -> dict:
    """Generate BGM with automatic emotion segmentation.

    Args:
        script_text: The script content
        title: Track title
        out_dir: Output directory
        config: BGM config
        use_auto_segments: If True, auto-detect emotional shifts and generate segments
        force_single_segment: If True, skip segmentation and use single-track mode
    """
    cfg = config or Config()
    cfg.ensure_dirs()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 分析剧本
    analysis = analyze_script_structured(script_text, title, cfg)
    analysis["title"] = title

    print(f"\n[{title}] 分析结果:")
    print(f"  主基调: {analysis['primary_tone']}")
    print(f"  总时长: {analysis.get('total_duration', 0)}s")
    print(f"  场景数: {len(analysis.get('timeline', []))}")

    # 检测情绪分段
    if force_single_segment:
        segments = [Segment(
            tone=analysis["primary_tone"],
            start_s=0,
            end_s=analysis.get("total_duration", 80),
            duration=analysis.get("total_duration", 80),
            intensity=analysis["primary_intensity"],
            description="Single segment (forced)"
        )]
    elif use_auto_segments:
        segments = detect_emotional_segments(analysis)
    else:
        segments = [Segment(
            tone=analysis["primary_tone"],
            start_s=0,
            end_s=analysis.get("total_duration", 80),
            duration=analysis.get("total_duration", 80),
            intensity=analysis["primary_intensity"],
            description="Single segment (auto-segment disabled)"
        )]

    print(f"\n[{title}] 检测到 {len(segments)} 个情绪段:")
    for i, seg in enumerate(segments):
        print(f"  段{i+1}: {seg.start_s}-{seg.end_s}s ({seg.duration}s) | {seg.tone} | 强度{seg.intensity}")

    # 如果只有一段，使用标准 pipeline
    if len(segments) == 1:
        print(f"\n[{title}] 单情绪段，使用标准 pipeline...")
        from .pipeline import generate_bgm_v2
        return generate_bgm_v2(analysis, out_dir, use_stinger=True, config=cfg)

    # 多段：分别生成然后拼接
    print(f"\n[{title}] 多情绪段，分段生成...")
    client = SunoClient(cfg)
    segment_files = []

    for i, seg in enumerate(segments):
        print(f"\n[{title}] 生成段{i+1}/{len(segments)}: {seg.tone} ({seg.duration}s)")

        params = TONE_PARAMS.get(seg.tone, TONE_PARAMS["紧张"])
        bpm = pick_bpm(seg.tone, seg.intensity)
        key = params.key_options[0]

        tags = f"{params.tags_seed}, {bpm}bpm, {key}"
        if len(tags) > 120:
            tags = tags[:117] + "..."

        prompt = (
            f"[Instrumental, score only]\n"
            f"A {params.name_en} cinematic cue at {bpm}bpm in {key}.\n"
            f"Core instrumentation: {', '.join(params.instrumentation[:3])}.\n"
            f"Production style: {params.production_style}.\n"
            f"Duration: ~{seg.duration}s. "
            f"Do not include any vocals, singing, or lyrics."
        )

        payload = {
            "prompt": prompt,
            "tags": tags,
            "title": f"{title}_seg{i+1}",
            "mv": "chirp-v4",
            "make_instrumental": True,
        }

        candidates = client.generate(payload, cache=True)
        target_bpm = bpm
        scored = [score_candidate(p, target_bpm) for p in candidates]
        scored.sort(key=lambda m: m["score"], reverse=True)
        best = Path(scored[0]["path"])

        print(f"  Tags: {tags}")
        print(f"  选择: {best.name}")

        # 后处理
        trimmed = out_dir / f"seg{i+1}_trimmed.mp3"
        fade_out = 3000 if i == len(segments) - 1 else 0  # 最后一段加 fade out
        fade_and_normalize(best, seg.duration, target_lufs=-18, fade_out_ms=fade_out, out_path=trimmed)
        segment_files.append(trimmed)

    # 拼接
    print(f"\n[{title}] 拼接 {len(segment_files)} 段 (3秒 crossfade)...")
    final_path = out_dir / f"{title}_segmented.mp3"
    crossfade_segments(segment_files, crossfade_ms=3000, out_path=final_path)

    result = {
        "pipeline": "auto_segmented",
        "segments_detected": len(segments),
        "segments": [
            {
                "tone": s.tone,
                "start_s": s.start_s,
                "end_s": s.end_s,
                "duration": s.duration,
                "intensity": s.intensity,
            } for s in segments
        ],
        "analysis": analysis,
        "final_audio": str(final_path),
    }

    # 保存元数据
    meta_path = out_dir / f"{title}_metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[{title}] 完成: {final_path}")
    return result


# 导出给外部使用
__all__ = ['generate_segmented_bgm', 'detect_emotional_segments', 'Segment']
