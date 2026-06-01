"""BGM v2 — Suno-aware, storyboard-driven BGM pipeline."""
import os

# Set ffmpeg/ffprobe path for Windows (must be before pydub import)
FFMPEG_DIR = r"C:\Users\99384\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(FFMPEG_DIR, "ffprobe.exe")

# 设置 PATH 环境变量
if os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

# 必须在导入 pydub 之前设置
from pydub import AudioSegment
if os.path.exists(FFMPEG_PATH):
    AudioSegment.converter = FFMPEG_PATH
if os.path.exists(FFPROBE_PATH):
    AudioSegment.ffprobe = FFPROBE_PATH

from .config import Config
from .tone_params import TONE_PARAMS, render_suno_payload, render_storyboard_payload
from .gpt_analyzer import analyze_script_structured, normalize_tone
from .storyboard import analyze_storyboard
from .suno_prompt_builder import build_suno_prompts, build_unified_prompt
from .suno_client import SunoClient
from .quality import vocal_energy_ratio, detect_bpm, score_candidate
from .post import fade_and_normalize, crossfade_segments
from .pipeline import (
    generate_bgm_v2,
    generate_bgm_legacy_style,
    generate_bgm_from_storyboard,
)
from .multisegment_pipeline import (
    generate_bgm_multisegment,
    detect_emotional_cues,
)
