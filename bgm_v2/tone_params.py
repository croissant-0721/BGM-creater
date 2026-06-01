"""Music-theory grounded params per emotional tone.

GPT only picks tone + intensity; the *hard* params are looked up here so the
prompt becomes deterministic and Suno-friendly.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ToneParams:
    name_en: str
    bpm_range: Tuple[int, int]
    key_options: List[str]
    instrumentation: List[str]
    production_style: str
    forbidden: List[str]
    tags_seed: str  # short positive-only tag string, ~80-100 chars


TONE_PARAMS: Dict[str, ToneParams] = {
    "紧张": ToneParams(
        name_en="tense",
        bpm_range=(120, 140),
        key_options=["D minor", "A minor", "E minor"],
        instrumentation=[
            "ostinato strings", "sub bass drone",
            "metallic percussion", "low brass stabs",
        ],
        production_style="Hans Zimmer / Junkie XL, hybrid orchestral, sparse",
        forbidden=["major key", "acoustic guitar", "folk"],
        tags_seed="cinematic orchestral, dark suspense, ostinato strings, sub bass, hybrid percussion",
    ),
    "悬疑": ToneParams(
        name_en="mystery",
        bpm_range=(70, 90),
        key_options=["atonal", "C minor", "modal ambiguous"],
        instrumentation=[
            "dissonant pad", "prepared piano",
            "low drone", "sparse glockenspiel",
        ],
        production_style="Trent Reznor / Mica Levi, sound-design forward",
        forbidden=["drum kit", "melodic theme", "uplifting"],
        tags_seed="ambient mystery, atonal pad, prepared piano, low drone, sound design",
    ),
    "温馨": ToneParams(
        name_en="warm",
        bpm_range=(75, 95),
        key_options=["C major", "G major", "F Lydian"],
        instrumentation=[
            "felt piano", "warm strings",
            "wooden percussion", "soft pads",
        ],
        production_style="Ludovico Einaudi / Joe Hisaishi, intimate",
        forbidden=["distortion", "808 bass", "trap"],
        tags_seed="cinematic warm, felt piano, intimate strings, wooden percussion, gentle",
    ),
    "悲伤": ToneParams(
        name_en="sad",
        bpm_range=(60, 75),
        key_options=["A minor", "E minor", "F minor"],
        instrumentation=[
            "solo cello", "solo piano",
            "long reverb tail", "sparse strings",
        ],
        production_style="Max Richter / Johann Johannsson, minimalist",
        forbidden=["drum kit", "fast tempo", "uplifting"],
        tags_seed="cinematic melancholic, solo cello, piano, long reverb, minimalist",
    ),
    "恐惧": ToneParams(
        name_en="fear",
        bpm_range=(50, 70),
        key_options=["dissonant cluster", "B-flat minor"],
        instrumentation=[
            "low drone", "irregular percussion",
            "reversed piano", "wind texture",
        ],
        production_style="Mica Levi (Under the Skin), abstract horror",
        forbidden=["melodic theme", "major key", "epic"],
        tags_seed="horror score, dissonant drone, reversed piano, irregular hits, dread",
    ),
    "动作": ToneParams(
        name_en="action",
        bpm_range=(140, 170),
        key_options=["D minor", "F minor"],
        instrumentation=[
            "hybrid orchestral", "electronic drums",
            "brass stabs", "taiko",
        ],
        production_style="Lorne Balfe / Brian Tyler, propulsive",
        forbidden=["slow tempo", "solo piano", "acoustic ballad"],
        tags_seed="cinematic action, hybrid percussion, taiko, brass stabs, driving",
    ),
    "励志": ToneParams(
        name_en="uplifting",
        bpm_range=(100, 120),
        key_options=["C major", "D major", "F major"],
        instrumentation=[
            "rising strings", "french horns",
            "anthemic swell", "soft choir-like pad (no vocals)",
        ],
        production_style="Steve Jablonsky / Two Steps From Hell, hopeful",
        forbidden=["minor key", "atonal", "horror"],
        tags_seed="cinematic uplifting, rising strings, french horns, anthemic, hopeful",
    ),
    # ---- short-drama-specific tones (added for storyboard pipeline) ----
    "羞辱": ToneParams(
        name_en="humiliation",
        bpm_range=(85, 110),
        key_options=["C minor", "G minor", "B-flat minor"],
        instrumentation=[
            "sub bass pulse", "muted tight strings",
            "low piano clusters", "subtle heartbeat perc",
        ],
        production_style="K-drama OST antagonist cue, taut and oppressive",
        forbidden=["uplifting", "major key", "fast drums"],
        tags_seed="cinematic tense, sub bass pulse, muted strings, low piano, oppressive",
    ),
    "静默": ToneParams(
        name_en="silent_suspense",
        bpm_range=(50, 70),
        key_options=["atonal", "modal ambiguous", "single sustained pitch"],
        instrumentation=[
            "near silence", "very low drone",
            "single piano notes", "ultra-soft pad",
        ],
        production_style="held-breath moment, ultra minimalist score",
        forbidden=["drums", "melody", "loud", "fast tempo"],
        tags_seed="cinematic silence, low drone, sparse piano, held breath, minimal",
    ),
    "反击": ToneParams(
        name_en="comeback",
        bpm_range=(110, 130),
        key_options=["D minor", "A minor", "F minor"],
        instrumentation=[
            "driving strings ostinato", "trap-orchestral hybrid",
            "brass stabs", "taiko impact",
        ],
        production_style="trap-orchestral revenge cue, K-drama montage flavor",
        forbidden=["soft piano", "acoustic ballad", "slow"],
        tags_seed="trap orchestral, driving strings, brass stab, taiko, satisfying",
    ),
    "豪门": ToneParams(
        name_en="elite_pressure",
        bpm_range=(80, 100),
        key_options=["C minor", "E-flat minor", "G minor"],
        instrumentation=[
            "legato strings", "piano", "french horn",
            "soft sub bass",
        ],
        production_style="upper-class corporate drama, refined and cold",
        forbidden=["distortion", "EDM", "rock"],
        tags_seed="cinematic refined, legato strings, piano, french horn, cold luxury",
    ),
    "异常": ToneParams(
        name_en="anomalous",
        bpm_range=(60, 90),
        key_options=["dissonant cluster", "B-flat minor", "chromatic"],
        instrumentation=[
            "reversed strings", "very low drone",
            "metallic shimmer", "wide reverb pad",
        ],
        production_style="supernatural intrusion, sound-design hybrid",
        forbidden=["melodic theme", "major key", "uplifting"],
        tags_seed="anomalous score, reversed strings, low drone, metallic shimmer, eerie",
    ),
}


def pick_bpm(tone: str, intensity: int) -> int:
    """Map intensity 1..10 onto the tone's BPM range linearly."""
    params = TONE_PARAMS.get(tone, TONE_PARAMS["紧张"])
    lo, hi = params.bpm_range
    intensity = max(1, min(10, intensity))
    return int(lo + (hi - lo) * (intensity - 1) / 9)


def render_suno_payload(
    tone: str,
    intensity: int,
    total_duration_s: int,
    title: str,
    timeline: list | None = None,
) -> dict:
    """Build a Suno-friendly payload.

    Rules applied (P0):
    - tags = positive only, <=120 chars; no "no X" negatives.
    - prompt starts with [Instrumental, score only] bracket marker.
    - make_instrumental=true.
    - prompt body describes BPM/key/instrumentation + dynamics arc derived
      from timeline (if available) or a single arc otherwise.
    """
    params = TONE_PARAMS.get(tone, TONE_PARAMS["紧张"])
    bpm = pick_bpm(tone, intensity)
    key = params.key_options[0]

    tags = f"{params.tags_seed}, {bpm}bpm, {key}"
    if len(tags) > 120:
        tags = tags[:117] + "..."

    instr_line = ", ".join(params.instrumentation[:3])

    arc_lines = []
    if timeline:
        for i, seg in enumerate(timeline[:8]):  # 支持更多段
            t = seg.get("time_range", f"seg{i}")
            tone_seg = seg.get("emotional_tone", tone)
            inten = seg.get("intensity", intensity)
            sub = TONE_PARAMS.get(tone_seg, params)

            # 为每段写完整的乐器和风格描述
            seg_instr = ", ".join(sub.instrumentation[:3])
            seg_bpm = pick_bpm(tone_seg, inten)
            seg_key = sub.key_options[0] if sub.key_options else key

            arc_lines.append(
                f"[{t}] {sub.name_en} style (intensity {inten}/10):\n"
                f"  Instruments: {seg_instr}\n"
                f"  BPM: {seg_bpm}, Key: {seg_key}\n"
                f"  Production: {sub.production_style}"
            )
    else:
        arc_lines.append("- [0-15s] Sparse intro, minimal instruments")
        arc_lines.append("- [15-40s] Build tension, layer instruments gradually")
        arc_lines.append("- [40-60s] Climax with full orchestral intensity")
        arc_lines.append("- [60s-end] Resolve and fade")

    arc_block = "\n".join(arc_lines)

    # 超强无人声提示 - 放在开头和结尾
    no_vocals_header = (
        "*** INSTRUMENTAL ONLY - NO VOCALS ***\n"
        "This is PURE BACKGROUND MUSIC with ZERO human voice.\n"
        "NO singing, NO lyrics, NO vocal samples, NO choir, NO humming.\n"
    )

    no_vocals_footer = (
        "\n\n*** CRITICAL: NO VOCALS ***\n"
        "- NO singing voice\n"
        "- NO lyrics or words\n"
        "- NO vocal chops or samples\n"
        "- NO choir or backing vocals\n"
        "- NO humming or vocal pads\n"
        "- NO pitch-shifted vocals\n"
        "- ONLY orchestral/instrumental sounds\n"
        "- ALL sounds must be synthesized or acoustic instruments"
    )

    # 强调单轨连续
    continuous_block = (
        f"Create ONE {total_duration_s}-SECOND CONTINUOUS cinematic background score.\n"
        f"Single uninterrupted track - NO silences between sections.\n"
        f"Smooth transitions between emotional changes.\n"
        f"DO NOT generate multiple separate songs."
    )

    prompt = (
        f"{no_vocals_header}\n"
        f"{continuous_block}\n\n"
        f"Base: {params.name_en} cinematic, {bpm}BPM, {key}\n\n"
        f"TIMELINE (each section flows into the next):\n{arc_block}"
        f"{no_vocals_footer}"
    )

    return {
        "prompt": prompt,
        "tags": tags,
        "title": f"{title} - {params.name_en} BGM",
        "mv": "chirp-v4",
        "make_instrumental": True,
    }


def render_storyboard_payload(
    cues: list[dict],
    total_duration_s: int,
    title: str,
    primary_tone: str | None = None,
) -> dict:
    """Build Suno payload from a storyboard cue list.

    Args:
        cues: list of {start_s, end_s, tone, intensity_peak, narrative_summary, ...}.
              These are the music sections — typically 3-6 of them.
        total_duration_s: total BGM duration to target (exact match required downstream).
        title: track title (usually episode+scene identifier).
        primary_tone: optional override. If None, picks the cue tone with the longest
                      cumulative duration as the palette anchor.

    The anchor cue decides BPM/key/core instrumentation. The other cues are described
    in the dynamics arc inside the prompt body so Suno follows the emotional curve.
    """
    if not cues:
        return render_suno_payload(
            tone=primary_tone or "紧张", intensity=7,
            total_duration_s=total_duration_s, title=title, timeline=None,
        )

    if primary_tone is None:
        tone_duration: dict[str, int] = {}
        for c in cues:
            t = c.get("tone", "紧张")
            dur = max(0, c.get("end_s", 0) - c.get("start_s", 0))
            tone_duration[t] = tone_duration.get(t, 0) + dur
        primary_tone = max(tone_duration.items(), key=lambda kv: kv[1])[0]

    anchor = TONE_PARAMS.get(primary_tone, TONE_PARAMS["紧张"])
    peak_intensity = max((c.get("intensity_peak", 5) for c in cues), default=5)
    bpm = pick_bpm(primary_tone, peak_intensity)
    key = anchor.key_options[0]

    tags = f"{anchor.tags_seed}, {bpm}bpm, {key}"
    if len(tags) > 120:
        tags = tags[:117] + "..."

    instr_line = ", ".join(anchor.instrumentation[:3])

    arc_lines: list[str] = []
    for c in cues:
        sub = TONE_PARAMS.get(c.get("tone", primary_tone), anchor)
        seg_instr = ", ".join(sub.instrumentation[:3])
        seg_bpm = pick_bpm(c.get("tone", primary_tone), c.get("intensity_peak", 5))
        seg_key = sub.key_options[0] if sub.key_options else key

        arc_lines.append(
            f"[{c.get('start_s', 0)}-{c.get('end_s', 0)}s] {sub.name_en} style (intensity {c.get('intensity_peak', 5)}/10):\n"
            f"  Instruments: {seg_instr}\n"
            f"  BPM: {seg_bpm}, Key: {seg_key}"
        )

    # 超强无人声提示
    no_vocals_header = (
        "*** INSTRUMENTAL ONLY - NO VOCALS ***\n"
        "This is PURE BACKGROUND MUSIC with ZERO human voice.\n"
        "NO singing, NO lyrics, NO vocal samples, NO choir, NO humming.\n"
    )

    no_vocals_footer = (
        "\n\n*** CRITICAL: NO VOCALS ***\n"
        "- NO singing voice\n"
        "- NO lyrics or words\n"
        "- NO vocal chops or samples\n"
        "- NO choir or backing vocals\n"
        "- ONLY orchestral/instrumental sounds"
    )

    # 强调单轨连续
    continuous_block = (
        f"Create ONE {total_duration_s}-SECOND CONTINUOUS cinematic background score.\n"
        f"Single uninterrupted track - NO silences between sections.\n"
        f"Smooth transitions between emotional changes.\n"
        f"DO NOT generate multiple separate songs."
    )

    prompt = (
        f"{no_vocals_header}\n"
        f"{continuous_block}\n\n"
        f"Base: {anchor.name_en} cinematic, {bpm}BPM, {key}\n\n"
        f"TIMELINE (each section flows into the next):\n"
        + "\n".join(arc_lines)
        + no_vocals_footer
    )

    return {
        "prompt": prompt,
        "tags": tags,
        "title": f"{title} - {anchor.name_en} BGM",
        "mv": "chirp-v4",
        "make_instrumental": True,
    }
