"""BGM v2 — Suno-aware, storyboard-driven BGM pipeline."""
from .config import Config
from .tone_params import TONE_PARAMS, render_suno_payload, render_storyboard_payload
from .gpt_analyzer import analyze_script_structured
from .storyboard import analyze_storyboard
from .suno_client import SunoClient
from .quality import vocal_energy_ratio, detect_bpm, score_candidate
from .post import fade_and_normalize, crossfade_segments
from .pipeline import (
    generate_bgm_v2,
    generate_bgm_legacy_style,
    generate_bgm_from_storyboard,
)
