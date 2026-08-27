"""Test bgm_v2 pipeline on a user-supplied Episode 1 wedding script (no explicit timecodes)."""
from __future__ import annotations
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bgm_v2 import Config
from bgm_v2.gpt_analyzer import analyze_script_structured
from bgm_v2.pipeline import generate_bgm_v2
from bgm_v2.quality import vocal_energy_ratio, detect_bpm, measure_lufs
from bgm_v2.tone_params import pick_bpm

SCRIPT = """第 1 集

1-1
场景：纽约上东区五星级酒店宴会厅婚礼红毯 日 内
时间：婚礼进行中
人物：Mia Carter，Ethan Walker，Ava Walker，司仪，宾客
局势变化：信息释放 / 谎言暴露——Ethan 当众取消婚礼并污名化 Mia
过程描写：
Ethan 冷硬的声音压过婚礼誓词。大屏亮起：WALKER-CARTER WEDDING CANCELLED。
Ethan: "This wedding is over."
Mia 的手捧花轻轻下沉，笑容僵住。
Mia (低声): "Ethan... what is this?"
Ethan: "The truth. Mia Carter only wanted my name and my money."
宾客骚动，举手机拍。
Mia 向前一步: "You told me to walk down this aisle."
Ava 从花墙后走出，挽住 Ethan: "And he told me the truth before he made the worst mistake of his life."
Mia 看见 Ava 手上钻戒，手指攥紧花梗。

1-2
场景：五星级酒店宴会厅主桌旁
人物：Mia, Ethan, Ava, Walker 家律师, 宾客
局势变化：威胁升级 / 选择压力——Mia 被要求承担婚礼违约金，母亲疗养费被冻结
过程描写：
Ava 端起香槟逼近 Mia，杯沿贴近婚纱胸口。
Ava: "You still look pretty for a dumped bride." 香槟泼在象牙白婚纱上。
Mia (压怒): "Touch me again, Ava."
Walker 家律师把违约金文件夹塞到 Mia 面前：取消婚礼违约金八十万美元。
Mia: "I didn't cancel anything."
Mia 手机震动，屏幕显示：BELLEVUE CARE CENTER PAYMENT FROZEN。
Ethan: "My family paid your mother's bills. Not anymore."
Mia 脸色发白，宾客席传来压低的笑声。

1-3
场景：五星级酒店侧门走廊
人物：Mia, Ethan, Ava, Noah Reed (司机), 安保, 宾客
局势变化：关系变化 / 情绪转折——Noah 第一次介入，Mia 从被围猎转为逃离现场
过程描写：
Mia 抓裙摆冲出宴会厅，Ethan 追到走廊口。
Ethan: "Run, Mia. That's all you have left."
Mia 猛地停步: "No. You don't get to watch me break."
侧门旁 Noah 把深色司机外套披到 Mia 肩上挡住香槟湿痕。
Noah: "Keep walking."
Mia 第一次看清他制服胸牌：NOAH。
Ava (讥讽): "Oh my God. She found a driver."
Noah 推开侧门，雨光打进来: "Better than a coward in a tux."
Ethan 脸色沉下。Mia 抓紧 Noah 外套，迈出侧门。

钩子：被全纽约名流当众抛弃的 Mia，第一次被一个"司机"护住。可这个司机，似乎并不怕 Walker 家。
"""
TITLE = "ep1_wedding_runaway"


def measure_final(path: Path, target_bpm: int) -> dict:
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
    out_new = repo_root / "comparison" / "output_ep1"
    out_new.mkdir(parents=True, exist_ok=True)

    print("[ep1] >>> analyzing script with GPT...", flush=True)
    t0 = time.time()
    analysis = analyze_script_structured(SCRIPT, TITLE, cfg)
    analysis["title"] = TITLE
    (repo_root / "comparison" / "ep1_analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[ep1] GPT analysis done in {time.time()-t0:.1f}s", flush=True)
    print(f"[ep1] primary_tone={analysis['primary_tone']} intensity={analysis['primary_intensity']} total={analysis.get('total_duration')}s", flush=True)
    for seg in analysis.get("timeline", []):
        print(f"[ep1]   seg {seg.get('time_range')} -> {seg.get('emotional_tone')} {seg.get('intensity')}/10", flush=True)

    target_bpm = pick_bpm(analysis["primary_tone"], analysis["primary_intensity"])
    print(f"[ep1] target_bpm={target_bpm}", flush=True)

    print("[ep1] >>> running generate_bgm_v2 (this calls Suno)...", flush=True)
    t0 = time.time()
    result = generate_bgm_v2(analysis, out_new, use_stinger=True, config=cfg)
    result["elapsed_s"] = round(time.time() - t0, 1)
    result["final_metrics"] = measure_final(Path(result["final_audio"]), target_bpm)
    print(f"[ep1] pipeline finished in {result['elapsed_s']}s", flush=True)
    print(f"[ep1] final={result['final_audio']}", flush=True)
    print(f"[ep1] metrics={result['final_metrics']}", flush=True)

    out = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "script_title": TITLE,
        "analysis": analysis,
        "target_bpm": target_bpm,
        "result": result,
    }
    (repo_root / "comparison" / "ep1_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("[ep1] DONE wrote comparison/ep1_results.json", flush=True)


if __name__ == "__main__":
    main()
