"""A/B compare OLD vs NEW BGM pipelines on the same script.

Usage:
    python comparison/run_compare.py

Output:
    comparison/output_old/<...>.mp3
    comparison/output_new/<...>.mp3
    comparison/results.json   <- structured run log
"""
from __future__ import annotations
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bgm_v2 import Config
from bgm_v2.gpt_analyzer import analyze_script_structured
from bgm_v2.pipeline import generate_bgm_v2, generate_bgm_legacy_style
from bgm_v2.quality import score_candidate, vocal_energy_ratio, detect_bpm, measure_lufs
from bgm_v2.tone_params import pick_bpm

# ---------- sample script (same one shipped in bgm-timeline.html) ----------
SAMPLE_SCRIPT = """第1场（0-17s）
场景：地下冷柜区
过程描写：
Cade被绑在椅子上，满身是血。Evelyn冷冷地看着他。
Cade：你以为杀了我就能结束吗？

第2场（17-38s）
场景：同一空间
过程描写：
Evelyn轻笑，屏幕亮起数据曲线。
Evelyn: "Investors fund it. Politicians legalize it."
Cade盯着那些名单，眼神变冷。

第3场（38-59s）
场景：冷柜区前
过程描写：
Cade: "Then I don't just get out. I drag all of you into daylight."
安保微抬枪口。

第4场（59-80s）
场景：押返通道
过程描写：
Evelyn: "Keep him for the end."
Cade被扭身押回，眼神已经不是单纯活命。
"""
SAMPLE_TITLE = "episode_1_scene_1"


def measure_final(path: Path, target_bpm: int) -> dict:
    """Quality metrics on the final output that ships to user."""
    return {
        "path": str(path),
        "vocal_energy_ratio": round(vocal_energy_ratio(path), 4),
        "bpm_detected": round(detect_bpm(path), 1),
        "bpm_target": target_bpm,
        "lufs": (lambda v: round(v, 2) if v is not None else None)(measure_lufs(path)),
    }


def main() -> None:
    cfg = Config()
    cfg.ensure_dirs()
    repo_root = Path(__file__).resolve().parent.parent
    out_old = repo_root / "comparison" / "output_old"
    out_new = repo_root / "comparison" / "output_new"
    out_old.mkdir(parents=True, exist_ok=True)
    out_new.mkdir(parents=True, exist_ok=True)

    # ---- shared analysis (run once, reuse for both pipelines for fairness) ----
    analysis_cache = repo_root / "comparison" / "analysis_cache.json"
    if analysis_cache.exists():
        print(f"[run] reusing cached GPT analysis from {analysis_cache.name}")
        analysis = json.loads(analysis_cache.read_text(encoding="utf-8"))
    else:
        print("[run] analyzing script with GPT-5...")
        t0 = time.time()
        analysis = analyze_script_structured(
            SAMPLE_SCRIPT, SAMPLE_TITLE, cfg,
        )
        analysis["title"] = SAMPLE_TITLE
        analysis_cache.write_text(
            json.dumps(analysis, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[run] GPT analysis done in {time.time()-t0:.1f}s, cached")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))

    target_bpm = pick_bpm(analysis["primary_tone"], analysis["primary_intensity"])

    # ---- OLD pipeline ----
    print("\n[run] === OLD pipeline ===")
    t0 = time.time()
    old_result = generate_bgm_legacy_style(analysis, out_old, config=cfg)
    old_result["elapsed_s"] = round(time.time() - t0, 1)
    old_result["final_metrics"] = measure_final(Path(old_result["final_audio"]), target_bpm)
    print(f"[run] OLD final: {old_result['final_audio']}")
    print(f"[run] OLD metrics: {old_result['final_metrics']}")

    # ---- NEW pipeline ----
    print("\n[run] === NEW pipeline (v2) ===")
    t0 = time.time()
    new_result = generate_bgm_v2(analysis, out_new, use_stinger=True, config=cfg)
    new_result["elapsed_s"] = round(time.time() - t0, 1)
    new_result["final_metrics"] = measure_final(Path(new_result["final_audio"]), target_bpm)
    print(f"[run] NEW final: {new_result['final_audio']}")
    print(f"[run] NEW metrics: {new_result['final_metrics']}")

    # ---- dump results.json ----
    out = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "script_title": SAMPLE_TITLE,
        "analysis": analysis,
        "target_bpm": target_bpm,
        "old": old_result,
        "new": new_result,
    }
    (repo_root / "comparison" / "results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    print("\n[run] wrote comparison/results.json")


if __name__ == "__main__":
    main()
