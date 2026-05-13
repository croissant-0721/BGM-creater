"""BGM v2 — Suno-aware, timeline-driven BGM pipeline."""
from .config import Config
from .tone_params import TONE_PARAMS, render_suno_payload
from .gpt_analyzer import analyze_script_structured
from .suno_client import SunoClient
from .quality import vocal_energy_ratio, detect_bpm, score_candidate
from .post import fade_and_normalize, crossfade_segments
from .pipeline import generate_bgm_v2, generate_bgm_legacy_style
