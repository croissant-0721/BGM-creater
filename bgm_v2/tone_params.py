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
        for i, seg in enumerate(timeline[:6]):
            t = seg.get("time_range", f"seg{i}")
            tone_seg = seg.get("emotional_tone", tone)
            inten = seg.get("intensity", intensity)
            sub = TONE_PARAMS.get(tone_seg, params)
            arc_lines.append(
                f"- {t}: {sub.name_en} intensity {inten}/10, "
                f"emphasis on {sub.instrumentation[0]}"
            )
    else:
        arc_lines.append("- 0:00-0:15 sparse intro")
        arc_lines.append("- 0:15-0:40 build with layered instruments")
        arc_lines.append("- 0:40-end climax then resolve")

    arc_block = "\n".join(arc_lines)
    prompt = (
        f"[Instrumental, score only]\n"
        f"A {params.name_en} cinematic cue at {bpm}bpm in {key}.\n"
        f"Core instrumentation: {instr_line}.\n"
        f"Production style: {params.production_style}.\n"
        f"Dynamics arc across ~{total_duration_s}s:\n{arc_block}\n"
        f"Do not include any vocals, singing, or lyrics — orchestral score only."
    )

    return {
        "prompt": prompt,
        "tags": tags,
        "title": f"{title} - {params.name_en} BGM",
        "mv": "chirp-v4",
        "make_instrumental": True,
    }
