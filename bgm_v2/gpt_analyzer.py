"""GPT-driven script analyzer that returns structured music spec, not free-form prompt.

Output JSON shape:
{
    "primary_tone": "紧张",
    "primary_intensity": 7,
    "total_duration": 80,
    "emotional_arc": "...",
    "timeline": [
        {"time_range": "0-17s", "duration": 17, "scene_description": "...",
         "emotional_tone": "紧张", "intensity": 8,
         "stinger_at": null}  // or {"offset_s": 17, "type": "low_brass_hit"}
    ]
}
"""
from __future__ import annotations
import json
import re
import requests
from typing import Optional

from .config import Config
from .http_util import SESSION
from .tone_params import TONE_PARAMS

ALLOWED_TONES = list(TONE_PARAMS.keys())

SYSTEM_PROMPT = (
    "You are a senior film score composer and music supervisor. "
    "You read short-drama scripts and decompose them into emotional timelines "
    "with hard music parameters. Only output valid JSON, no prose."
)


def _build_user_prompt(script_text: str, script_title: str) -> str:
    return f"""Analyze the following short-drama scene script and return a JSON object.

Title: {script_title}

Script:
{script_text[:5000]}

Schema:
{{
  "primary_tone": one of {ALLOWED_TONES},
  "primary_intensity": integer 1..10,
  "total_duration": integer seconds (if the script has explicit time ranges like 0-17s use them),
  "emotional_arc": one-line description in Chinese,
  "tone_explanation": short Chinese explanation,
  "timeline": [
    {{
      "time_range": "0-17s",
      "duration": integer seconds,
      "scene_description": short Chinese summary,
      "emotional_tone": one of {ALLOWED_TONES},
      "intensity": integer 1..10,
      "stinger_at": null or {{"offset_s": integer seconds from segment start, "type": one of ["low_brass_hit","string_stab","sub_drop","perc_hit"]}}
    }}
  ]
}}

Hard rules:
- Total of segment durations must equal total_duration.
- Each emotional_tone must be from the allowed list. Pick the closest match.
- Add a stinger_at only when there is a clear in-scene shock or beat change.
- Respond with JSON only.
"""


def analyze_script_structured(
    script_text: str,
    script_title: str,
    config: Optional[Config] = None,
) -> dict:
    cfg = config or Config()
    payload = {
        "model": cfg.gpt_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(script_text, script_title)},
        ],
        "temperature": 0.6,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {cfg.gpt_api_key}",
        "Content-Type": "application/json",
    }
    r = SESSION.post(
        f"{cfg.gpt_api_base}/chat/completions",
        headers=headers, json=payload, timeout=90,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    data = json.loads(content)

    data["primary_tone"] = _coerce_tone(data.get("primary_tone"))
    data["primary_intensity"] = _coerce_intensity(data.get("primary_intensity"))
    if not data.get("total_duration"):
        data["total_duration"] = _extract_duration_fallback(script_text)
    for seg in data.get("timeline", []):
        seg["emotional_tone"] = _coerce_tone(seg.get("emotional_tone"))
        seg["intensity"] = _coerce_intensity(seg.get("intensity"))
    return data


def _coerce_tone(tone: Optional[str]) -> str:
    if tone in ALLOWED_TONES:
        return tone
    return "紧张"


def _coerce_intensity(v) -> int:
    try:
        x = int(v)
    except (TypeError, ValueError):
        return 5
    return max(1, min(10, x))


def _extract_duration_fallback(script_text: str) -> int:
    matches = re.findall(r"(\d+)\s*-\s*(\d+)\s*s", script_text)
    if not matches:
        return 80
    return max(int(end) for _, end in matches)
