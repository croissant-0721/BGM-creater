"""End-to-end pipelines.

generate_bgm_v2 — the new pipeline (Sprint 1+2+3).
generate_bgm_legacy_style — reproduces the OLD code's behavior so we can A/B.
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import Config
from .tone_params import (
    TONE_PARAMS, render_suno_payload, render_storyboard_payload, pick_bpm,
)
from .gpt_analyzer import analyze_script_structured
from .storyboard import analyze_storyboard
from .suno_client import SunoClient
from .quality import score_candidate
from .post import fade_and_normalize


# ----------------------------------------------------------------------
# Legacy reproduction — bug-for-bug compatible with test_bgm_timeline.py
# ----------------------------------------------------------------------

LEGACY_TONE_TAGS = {
    "紧张": "intense, suspense, dramatic, dark, aggressive, pounding, pressure",
    "悬疑": "mysterious, ambient, minimal, electronic, synthesizer, dark, atmospheric",
    "温馨": "warm, gentle, strings, melodic, atmospheric, cinematic",
    "悲伤": "melancholic, emotional, cello, slow, orchestral, atmospheric",
    "恐惧": "dark, ominous, threatening, deep, heavy, bass, danger, brooding",
    "动作": "intense, fast, aggressive, driving, relentless, action, chase",
    "励志": "uplifting, epic, cinematic, inspiring, orchestral",
}
LEGACY_TONE_DESC = {
    "紧张": "High-stakes confrontation, life or death situation",
    "悬疑": "Mystery and suspense",
    "温馨": "Warm emotional atmosphere",
    "悲伤": "Sad and emotional moment",
    "恐惧": "Fear and horror atmosphere",
    "动作": "Fast-paced action",
    "励志": "Uplifting and inspiring",
}


def _legacy_payload(tone: str, total_duration: int, title: str) -> dict:
    """Reproduces test_bgm_timeline.py's prompt/tag composition.

    NOTE the negative tags are intentional — matches the buggy old behavior
    we are trying to expose.
    """
    desc = LEGACY_TONE_DESC.get(tone, LEGACY_TONE_DESC["紧张"])
    tags = LEGACY_TONE_TAGS.get(tone, LEGACY_TONE_TAGS["紧张"])
    return {
        "prompt": f"[INSTRUMENTAL ONLY] {desc}",
        "tags": f"{tags}, no vocals, instrumental only",
        "title": f"{title} - {tone} BGM",
        "mv": "chirp-v4",
        "make_instrumental": True,
    }


def generate_bgm_legacy_style(
    analysis: dict,
    out_dir: Path,
    *,
    config: Optional[Config] = None,
) -> dict:
    """Old pipeline: 1 Suno call, take clips[0], brutal trim to duration. No fade, no LUFS."""
    cfg = config or Config()
    cfg.ensure_dirs()
    tone = analysis["primary_tone"]
    duration = analysis.get("total_duration", 80)
    title = analysis.get("title", "legacy")
    payload = _legacy_payload(tone, duration, title)

    client = SunoClient(cfg)
    files = client.generate(payload)
    chosen = files[0]  # legacy takes the first one, no scoring

    from pydub import AudioSegment
    audio = AudioSegment.from_mp3(str(chosen))
    target_ms = int(duration * 1000)
    if target_ms > 0 and target_ms < len(audio):
        audio = audio[:target_ms]  # brutal cut, no fade
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = out_dir / f"{tone}_{duration}s_legacy_{ts}.mp3"
    audio.export(str(final), format="mp3", bitrate="192k")

    return {
        "pipeline": "legacy",
        "payload": payload,
        "chosen_clip": str(chosen),
        "all_candidates": [str(p) for p in files],
        "final_audio": str(final),
        "post_processing": {
            "fade_out_ms": 0,
            "lufs_normalized": False,
        },
    }


# ----------------------------------------------------------------------
# New pipeline — Sprint 1 + 2 + 3
# ----------------------------------------------------------------------

def generate_bgm_v2(
    analysis: dict,
    out_dir: Path,
    *,
    use_stinger: bool = True,
    config: Optional[Config] = None,
) -> dict:
    """Full new pipeline.

    Steps:
      1. Build Suno payload from tone_params lookup + timeline.
      2. Suno generate (2 candidates).
      3. Score candidates: vocal energy + BPM match -> pick best.
      4. (optional) Generate a short stinger track for the strongest
         emotional-shift point and overlay it.
      5. Trim to duration, 3s fade-out, normalize to -18 LUFS.
    """
    cfg = config or Config()
    cfg.ensure_dirs()
    title = analysis.get("title", "v2")
    tone = analysis["primary_tone"]
    intensity = analysis["primary_intensity"]
    duration = analysis.get("total_duration", 80)
    timeline = analysis.get("timeline") or []
    target_bpm = pick_bpm(tone, intensity)

    # --- main track ---
    payload = render_suno_payload(
        tone=tone, intensity=intensity,
        total_duration_s=duration, title=title,
        timeline=timeline,
    )
    client = SunoClient(cfg)
    candidates = client.generate(payload)

    # --- score & pick best ---
    scored = [score_candidate(p, target_bpm) for p in candidates]
    scored.sort(key=lambda m: m["score"], reverse=True)
    best = Path(scored[0]["path"])
    print(f"[v2] candidates scored: {[(s['path'].split('/')[-1], s['score']) for s in scored]}")

    # --- stinger overlay ---
    stinger_info = None
    main_track = best
    if use_stinger and timeline:
        stinger_info = _maybe_overlay_stinger(
            main_track, timeline, cfg, out_dir, title,
        )
        if stinger_info and stinger_info.get("output"):
            main_track = Path(stinger_info["output"])

    # --- post-process ---
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = out_dir / f"{tone}_{duration}s_v2_{ts}.mp3"
    fade_and_normalize(
        main_track,
        target_duration_s=duration,
        target_lufs=cfg.target_lufs,
        fade_out_ms=cfg.fade_out_ms,
        out_path=final,
    )

    return {
        "pipeline": "v2",
        "payload": payload,
        "candidates": scored,
        "chosen_clip": str(best),
        "stinger": stinger_info,
        "final_audio": str(final),
        "post_processing": {
            "fade_out_ms": cfg.fade_out_ms,
            "lufs_normalized": True,
            "target_lufs": cfg.target_lufs,
        },
    }


# ----------------------------------------------------------------------
# Storyboard-driven pipeline — shot-aware, no stinger (SFX is the video model's job)
# ----------------------------------------------------------------------

def generate_bgm_from_storyboard(
    storyboard_text: str,
    title: str,
    out_dir: Path,
    *,
    config: Optional[Config] = None,
    duration_override: Optional[int] = None,
) -> dict:
    """Storyboard-aware BGM pipeline.

    Steps:
      1. GPT parses the storyboard table → shots[] + cues[] + primary_tone.
      2. render_storyboard_payload builds a Suno prompt whose dynamics arc
         walks through every cue (so the single track responds to the full
         emotional curve, not just the dominant tone).
      3. Suno 2-candidate generation, score on vocal-energy + BPM match.
      4. Strict-duration trim + 3s fade-out + LUFS normalize to -18.
      5. No stinger overlay — SFX (thunder, glass, screams) is generated
         by the video model, not BGM.
    """
    cfg = config or Config()
    cfg.ensure_dirs()

    analysis = analyze_storyboard(storyboard_text, title, cfg)
    total = duration_override or analysis["total_duration_s"]
    primary_tone = analysis["primary_tone"]
    cues = analysis["cues"]
    target_bpm = pick_bpm(primary_tone, analysis["primary_intensity"])

    payload = render_storyboard_payload(
        cues=cues,
        total_duration_s=total,
        title=title,
        primary_tone=primary_tone,
    )

    client = SunoClient(cfg)
    candidates = client.generate(payload)
    scored = [score_candidate(p, target_bpm) for p in candidates]
    scored.sort(key=lambda m: m["score"], reverse=True)
    best = Path(scored[0]["path"])

    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = out_dir / f"{primary_tone}_{total}s_sb_{ts}.mp3"
    fade_and_normalize(
        best,
        target_duration_s=total,
        target_lufs=cfg.target_lufs,
        fade_out_ms=cfg.fade_out_ms,
        out_path=final,
        strict_duration=True,
    )

    # measure final length so we can prove the duration match
    try:
        from pydub import AudioSegment as _AS
        final_ms = len(_AS.from_mp3(str(final)))
    except Exception:
        final_ms = None

    return {
        "pipeline": "storyboard",
        "analysis": analysis,
        "payload": payload,
        "candidates": scored,
        "chosen_clip": str(best),
        "final_audio": str(final),
        "target_duration_s": total,
        "final_duration_ms": final_ms,
        "duration_delta_ms": (final_ms - total * 1000) if final_ms is not None else None,
        "post_processing": {
            "fade_out_ms": cfg.fade_out_ms,
            "lufs_normalized": True,
            "target_lufs": cfg.target_lufs,
            "strict_duration": True,
        },
    }


def _maybe_overlay_stinger(
    main_track: Path,
    timeline: list,
    cfg: Config,
    out_dir: Path,
    title: str,
) -> Optional[dict]:
    """Find biggest intensity jump between segments, overlay a short stinger
    at that boundary. If no significant jump, return None."""
    if len(timeline) < 2:
        return None

    # find biggest jump
    biggest = None
    for i in range(1, len(timeline)):
        prev = timeline[i - 1].get("intensity", 5)
        cur = timeline[i].get("intensity", 5)
        delta = cur - prev
        if biggest is None or abs(delta) > abs(biggest[2]):
            biggest = (i, timeline[i], delta)

    # In short-drama beats, even a +/-1 intensity shift is a real "tell" moment
    # (a smirk, a reveal, a gun raise). Use 1 as the threshold instead of 2.
    if biggest is None or abs(biggest[2]) < 1:
        return None

    i, seg, delta = biggest
    boundary_s = sum(
        timeline[k].get("duration", 0) for k in range(i)
    )
    stinger_tone = seg.get("emotional_tone", "动作")
    stinger_intensity = min(10, seg.get("intensity", 7) + 1)

    # short ~8s stinger
    stinger_payload = render_suno_payload(
        tone=stinger_tone,
        intensity=stinger_intensity,
        total_duration_s=8,
        title=f"{title}-stinger",
        timeline=None,
    )
    # bias prompt toward percussive single hit
    stinger_payload["prompt"] = (
        f"[Instrumental, score only]\n"
        f"A short 6-8 second cinematic stinger cue for an emotional shift.\n"
        f"Single dramatic hit: low brass + sub bass drop + percussive impact, "
        f"then short ringing tail. No melody. {stinger_tone} flavor."
    )

    try:
        client = SunoClient(cfg)
        cands = client.generate(stinger_payload)
        stinger_clip = cands[0]
    except Exception as e:
        print(f"[v2] stinger generation failed, skipping: {e}")
        return None

    # overlay: lay stinger at boundary_s within the main track, ducked -3dB
    from pydub import AudioSegment
    main = AudioSegment.from_mp3(str(main_track))
    sting = AudioSegment.from_mp3(str(stinger_clip))[:8000].fade_in(120).fade_out(2000) - 3
    boundary_ms = max(0, int(boundary_s * 1000) - 400)  # land just before the cut
    if boundary_ms < len(main):
        overlaid = main.overlay(sting, position=boundary_ms)
    else:
        overlaid = main
    out_path = out_dir / f"main_with_stinger_{boundary_s}s.mp3"
    overlaid.export(str(out_path), format="mp3", bitrate="192k")
    return {
        "boundary_s": boundary_s,
        "tone": stinger_tone,
        "intensity": stinger_intensity,
        "stinger_clip": str(stinger_clip),
        "output": str(out_path),
        "intensity_delta": delta,
    }
