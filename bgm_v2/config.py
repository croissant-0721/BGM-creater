"""Centralized config — all secrets come from env. See bgm_v2/.env.example.

NOTE: previous in-repo code (test_bgm_timeline.py, CLAUDE.md) hardcoded keys.
We deliberately do NOT do that here; running the pipeline requires you to
export BGM_GPT_API_KEY and BGM_SUNO_API_KEY first (or source a .env file).
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    gpt_api_key: str = field(default_factory=lambda: os.getenv("BGM_GPT_API_KEY", ""))
    gpt_api_base: str = field(default_factory=lambda: os.getenv(
        "BGM_GPT_API_BASE", "https://yunwu.ai/v1"
    ))
    gpt_model: str = field(default_factory=lambda: os.getenv("BGM_GPT_MODEL", "gpt-5"))

    suno_api_key: str = field(default_factory=lambda: os.getenv("BGM_SUNO_API_KEY", ""))
    suno_api_base: str = field(default_factory=lambda: os.getenv(
        "BGM_SUNO_API_BASE", "https://api.bltcy.ai/suno"
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

    suno_poll_timeout_s: int = 300
    suno_poll_interval_s: int = 10
    suno_max_retries: int = 3

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
