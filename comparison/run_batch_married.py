"""Batch BGM run on MARRIED_THE_DRIVER episodes with diverse emotional tones.

Picks 4 episodes that should land in distinct BGM territories:
    Ep01 — wedding humiliation       → expect 羞辱/紧张
    Ep12 — observed cohabitation     → expect 静默/悬疑
    Ep13 — mother forced-transfer    → expect 悲伤/紧迫
    Ep30 — final boardroom vote      → expect 反击/动作
"""
from __future__ import annotations
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bgm_v2 import Config
from bgm_v2.pipeline import generate_bgm_from_storyboard
from bgm_v2.quality import vocal_energy_ratio, detect_bpm, measure_lufs
from bgm_v2.tone_params import pick_bpm

EPISODES = [
    ("ep01", "married_ep01_wedding_humiliation",
     "/tmp/married_eps/ep01.txt", "羞辱/紧张"),
    ("ep12", "married_ep12_cohab_observation",
     "/tmp/married_eps/ep12.txt", "静默/悬疑"),
    ("ep13", "married_ep13_mother_transfer",
     "/tmp/married_eps/ep13.txt", "悲伤/紧迫"),
    ("ep30", "married_ep30_final_vote",
     "/tmp/married_eps/ep30.txt", "反击/动作"),
]


def measure_final(path: Path, target_bpm: int) -> dict:
    return {
        "path": str(path),
        "vocal_energy_ratio": round(vocal_energy_ratio(path), 4),
        "bpm_detected": round(detect_bpm(path), 1),
        "bpm_target": target_bpm,
        "lufs": (lambda v: round(v, 2) if v is not None else None)(measure_lufs(path)),
    }


def run_one(ep_id: str, title: str, script_path: str, expected: str, cfg: Config, out_dir: Path) -> dict:
    print(f"\n[batch] >>> {ep_id} ({expected}) — {title}", flush=True)
    storyboard = Path(script_path).read_text(encoding="utf-8")
    print(f"[batch]    storyboard length = {len(storyboard)} chars", flush=True)
    t0 = time.time()
    result = generate_bgm_from_storyboard(
        storyboard_text=storyboard,
        title=title,
        out_dir=out_dir,
        config=cfg,
    )
    elapsed = round(time.time() - t0, 1)
    analysis = result["analysis"]
    print(f"[batch]    GPT picked primary_tone={analysis['primary_tone']} "
          f"intensity={analysis['primary_intensity']} total={analysis['total_duration_s']}s "
          f"cues={len(analysis['cues'])}", flush=True)
    for c in analysis["cues"]:
        print(f"[batch]      cue {c['id']} {c['start_s']:>3}-{c['end_s']:>3}s "
              f"{c['tone']:<6} peak={c['intensity_peak']}/10: "
              f"{(c.get('narrative_summary') or '')[:55]}", flush=True)

    target_bpm = pick_bpm(analysis["primary_tone"], analysis["primary_intensity"])
    result["final_metrics"] = measure_final(Path(result["final_audio"]), target_bpm)
    result["elapsed_s"] = elapsed
    result["expected_tone"] = expected
    print(f"[batch]    metrics={result['final_metrics']}", flush=True)
    print(f"[batch]    duration delta = {result['duration_delta_ms']}ms (target {result['target_duration_s']}s)", flush=True)
    print(f"[batch]    output = {result['final_audio']}", flush=True)
    return {
        "ep_id": ep_id,
        "title": title,
        "expected_tone": expected,
        "elapsed_s": elapsed,
        "result": result,
    }


def main() -> None:
    cfg = Config()
    cfg.ensure_dirs()
    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "comparison" / "output_married"
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = []
    overall_t0 = time.time()
    for ep_id, title, script_path, expected in EPISODES:
        try:
            runs.append(run_one(ep_id, title, script_path, expected, cfg, out_dir))
        except Exception as e:
            print(f"[batch] !! {ep_id} failed: {type(e).__name__}: {e}", flush=True)
            runs.append({
                "ep_id": ep_id, "title": title, "expected_tone": expected,
                "error": f"{type(e).__name__}: {e}",
            })

    out = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "total_elapsed_s": round(time.time() - overall_t0, 1),
        "runs": runs,
    }
    (repo_root / "comparison" / "married_batch_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print(f"\n[batch] DONE all in {out['total_elapsed_s']}s — wrote comparison/married_batch_results.json", flush=True)

    print("\n[batch] === SUMMARY ===", flush=True)
    print(f"{'ep':<6}{'tone(GPT)':<12}{'expected':<14}{'len':<6}{'vocal':<8}{'bpm':<6}{'LUFS':<8}{'delta_ms':<10}", flush=True)
    for r in runs:
        if "error" in r:
            print(f"{r['ep_id']:<6}!! ERROR: {r['error']}", flush=True)
            continue
        m = r["result"]["final_metrics"]
        a = r["result"]["analysis"]
        print(
            f"{r['ep_id']:<6}{a['primary_tone']:<12}{r['expected_tone']:<14}"
            f"{a['total_duration_s']:<6}{m['vocal_energy_ratio']:<8}{m['bpm_detected']:<6}"
            f"{m['lufs']:<8}{r['result']['duration_delta_ms']!s:<10}",
            flush=True,
        )


if __name__ == "__main__":
    main()
