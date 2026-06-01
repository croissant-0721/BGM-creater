# bgm_v2 — Suno-aware BGM pipeline

A drop-in replacement for `test_bgm_timeline.py` that implements the
optimization plan in `BGM-分析与优化方案.md`.

## What's new

| Capability | Old (`test_bgm_timeline.py`) | New (`bgm_v2/`) |
|---|---|---|
| Timeline → music | Collected but unused | Drives prompt arc + stinger overlay |
| Suno `tags` | Mixed positive + `no vocals` (counterproductive) | Positive-only, ≤120 chars |
| Prompt prefix | `[INSTRUMENTAL ONLY]` only | `[Instrumental, score only]` + BPM/key/instrument spec |
| Candidate handling | Take `clips[0]` | Download all, score, pick best |
| Quality gating | None | Vocal-energy heuristic + BPM match |
| Retries | None | 3× exponential backoff |
| Caching | None | SHA-256 payload → file |
| Trim | Brutal cut | `fade_out(3s)` + LUFS normalize to -18 |
| API keys | Hardcoded | Env vars (legacy fallback for local dev) |
| Stinger overlay | None | Auto at biggest intensity jump |

## Quick start

```bash
# 1. (recommended) set env vars to override hardcoded fallbacks
cp bgm_v2/.env.example .env
# edit .env, then:
export $(grep -v '^#' .env | xargs)

# 2. install deps
pip install flask flask-cors requests pydub librosa pyloudnorm soundfile

# 3. brew install ffmpeg   # macOS

# 4. run A/B compare
python3 comparison/run_compare.py
```

Outputs:

- `comparison/output_old/*.mp3` — legacy pipeline result
- `comparison/output_new/*.mp3` — new pipeline result
- `comparison/cache/*.mp3` — raw Suno candidates (both per call)
- `comparison/results.json` — full structured log including all metrics

## Module layout

```
bgm_v2/
├── __init__.py            # public exports
├── config.py              # env-driven Config dataclass
├── tone_params.py         # the 7-tone music-theory lookup + render_suno_payload
├── gpt_analyzer.py        # script → structured JSON (no free-form prompt)
├── suno_client.py         # submit + poll + retry + cache + dual download
├── quality.py             # vocal_energy_ratio, detect_bpm, score_candidate
├── post.py                # fade_and_normalize + crossfade_segments
└── pipeline.py            # generate_bgm_v2  +  generate_bgm_legacy_style
```

## How to use programmatically

```python
from bgm_v2 import Config
from bgm_v2.gpt_analyzer import analyze_script_structured
from bgm_v2.pipeline import generate_bgm_v2
from pathlib import Path

cfg = Config()
analysis = analyze_script_structured(script_text, title="ep1_s1", config=cfg)
analysis["title"] = "ep1_s1"
result = generate_bgm_v2(analysis, Path("output/"), use_stinger=True, config=cfg)
print(result["final_audio"])           # final mp3 path
print(result["candidates"])            # per-candidate metrics
print(result["stinger"])               # overlay metadata or None
```
