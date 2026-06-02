"""Centralized config — all secrets come from env. See bgm_v2/.env.example.

NOTE: previous in-repo code (test_bgm_timeline.py, CLAUDE.md) hardcoded keys.
We deliberately do NOT do that here; running the pipeline requires you to
export BGM_GPT_API_KEY and BGM_SUNO_API_KEY first (or source a .env file).
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


@dataclass
class Config:
    gpt_api_key: str = field(default_factory=lambda: os.getenv("BGM_GPT_API_KEY", ""))
    gpt_api_base: str = field(default_factory=lambda: os.getenv(
        "BGM_GPT_API_BASE", "https://yunwu.ai/v1"
    ))
    gpt_model: str = field(default_factory=lambda: os.getenv("BGM_GPT_MODEL", "gpt-5.4"))

    suno_api_key: str = field(default_factory=lambda: os.getenv("BGM_SUNO_API_KEY", ""))
    suno_api_base: str = field(default_factory=lambda: os.getenv(
        "BGM_SUNO_API_BASE", "https://yunwu.ai/suno"
    ))
    suno_model: str = field(default_factory=lambda: os.getenv("BGM_SUNO_MODEL", "chirp-v4"))

    output_dir: Path = field(default_factory=lambda: Path(
        os.getenv("BGM_OUTPUT_DIR", "comparison/output_new")
    ))
    cache_dir: Path = field(default_factory=lambda: Path(
        os.getenv("BGM_CACHE_DIR", "comparison/cache")
    ))
    target_lufs: float = -18.0
    fade_out_ms: int = 3000

    suno_poll_timeout_s: int = 900  # 15分钟（多段生成需要更长时间）
    suno_poll_interval_s: int = 15  # 降低轮询频率，减少API压力
    suno_max_retries: int = 5  # 增加重试次数

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
