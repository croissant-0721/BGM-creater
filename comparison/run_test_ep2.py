"""Storyboard-aware BGM run on Episode 2 (21-shot wedding showdown, 80s).

This is the test for the new pipeline:
    generate_bgm_from_storyboard
which:
  - Parses the storyboard table into shots[] + cues[] via GPT
  - Picks a primary tone from the expanded short-drama tone palette
  - Generates ONE Suno main track whose dynamics arc walks every cue
  - Trims to exactly the storyboard total duration (no stinger, no SFX)
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

# 21-shot storyboard transcribed verbatim from the user's PDF/screenshots.
STORYBOARD = """第 2 集分镜

| 镜号 | 时间 | 时长 | 画面描述 | 中英双语台词 | 运镜/景别 | 人物/场景 | 备注 |
| 1 | 0-4s | 4s | 红毯中央近景，Clara 仍握着 Ethan 带血的手，Victor 脸色沉下逼近。叙事功能：钩子/冲突 | Victor: "You're choosing a waiter over me?" / "你要选一个服务生，不选我？" | 固定中近景 | Clara、Ethan、Victor / 宴会厅 | SFX: 宾客抽气，远处酒杯轻碰 |
| 2 | 4-8s | 4s | Clara 不松手，正面直视 Victor。叙事功能：反应/钩子 | Clara: "I'm choosing not to marry you." / "我选不嫁给你。" | 正面近景 | Clara / 宴会厅红毯 | 婚纱、妆发延续上集 |
| 3 | 8-12s | 4s | Monica 冲上来指着 Clara，Gregory 站侧后冷压场。叙事功能：冲突/信息 | Monica: "Clara, stop acting like trash from foster care!" / "Clara，别像寄养家庭出来的垃圾一样丢人！" | 中景 | Monica、Clara、Gregory / 宴会厅 | SFX: 宾客骚动 |
| 4 | 12-16s | 4s | Gregory 盯住 Clara 和 Ethan 相握的手，低声命令。叙事功能：冲突 | Gregory: "Let go of him. Now." / "放开他。现在。" | 近景 | Gregory / 宴会厅 | 语气压低更危险 |
| 5 | 16-20s | 4s | Victor 嫌恶看向地毯血迹，伴郎团在后景嗤笑。叙事功能：冲突/信息 | Victor: "Look at him. He's bleeding on my carpet." / "看看他，他把血都弄到我的地毯上了。" | 低角度中近景 | Victor、伴郎、Ethan / 宴会厅 | 血迹与红毯可见 |
| 6 | 20-24s | 4s | 伴郎俯看 Ethan，故意笑出声。叙事功能：冲突 | Best Man: "The help got lucky." / "一个服务生走狗屎运了。" | 俯拍近景 | 伴郎、Ethan / 宴会厅 | 羞辱感延续 |
| 7 | 24-28s | 4s | Ethan 从地上缓缓站起，湿制服贴身，抬眼只看 Clara。叙事功能：转折/反应 | Ethan: "You sure?" / "你确定？" | 推近中景 | Ethan、Clara / 宴会厅 | 伤口、湿衬衫延续 |
| 8 | 28-32s | 4s | Clara 看着 Ethan，余光扫过 Victor。叙事功能：信息/反应 | Clara: "No. But I'm sure about him." / "不确定。但我确定不要他。" | 正反打近景 | Clara / 宴会厅 | 情绪冷决 |
| 9 | 32-36s | 4s | Victor 猛抓 Clara 手腕往回拽，婚纱袖口被扯紧。叙事功能：动作/冲突 | Victor: "You belong to me after tonight." / "今晚之后，你就是我的。" | 跟拍中近景 | Victor、Clara / 宴会厅 | SFX: 布料绷紧 |
| 10 | 36-40s | 4s | Ethan 一把扣住 Victor 手腕掰开，Victor 吃痛松手。叙事功能：反转/结果 | Ethan: "She said no." / "她说不。" | 手部特写拉到双人近景 | Ethan、Victor、Clara / 宴会厅 | SFX: 骨节受力声 |
| 11 | 40-43s | 3s | 吊灯轻晃，桌上银叉震颤，窗外晴空滚出闷雷，宾客全静。叙事功能：异常/反应 | Guest: "Was that thunder?" / "刚才是雷声？" | 道具特写组接 | 吊灯、银叉、宾客 / 宴会厅 | SFX: 金属震颤、闷雷 |
| 12 | 43-47s | 4s | Clara 低头看两人交握的手，再看 Ethan，压迫感减轻。叙事功能：关键揭示/反应 | （无台词） | 手部特写 | Clara、Ethan / 宴会厅 | 关键触碰可读 |
| 13 | 47-51s | 4s | Monica 失声指向 Ethan；Clara 冷冷顶回去。叙事功能：冲突/信息 | Monica: "He's dangerous!" Clara: "So is Victor." / "他很危险！" "Victor 也一样。" | 中近景双人 | Monica、Clara / 宴会厅 | banter 合并 |
| 14 | 51-55s | 4s | Victor 转头暴怒，Caleb 已带安保冲入厅门。叙事功能：紧迫感/动作 | Victor: "Security!" / "保安！" | 摇镜到厅门中景 | Victor、Caleb、安保 / 宴会厅 | SFX: 脚步急冲 |
| 15 | 55-59s | 4s | Caleb 逼近 Ethan，安保左右散开包围。叙事功能：冲突 | Caleb: "Step away from the bride, busboy." / "离新娘远点，端盘子的。" | 中景 | Caleb、Ethan、安保 / 宴会厅 | 站位形成围堵 |
| 16 | 59-63s | 4s | Clara 上前半步挡在 Ethan 侧前，盯住 Caleb。叙事功能：冲突/决定 | Clara: "Touch him, and I walk." / "碰他，我就走。" | 中近景 | Clara、Ethan、Caleb / 宴会厅 | Clara 首次公开护他 |
| 17 | 63-67s | 4s | Monica 讥笑抬手点向 Clara 脚上高跟鞋；Clara 低头一瞥。叙事功能：冲突/铺垫 | Monica: "Honey, you don't even own the shoes you're standing in." / "亲爱的，你脚上的鞋都不是你的。" | 近景 | Monica、Clara / 宴会厅 | 高跟鞋入画 |
| 18 | 67-70s | 3s | Clara 直接踢掉两只婚鞋，赤脚踩上红毯；全场倒吸气。叙事功能：关键动作/转折 | Clara: "Keep them." / "留给你们。" | 下摇到脚部特写再抬起 | Clara / 宴会厅 | SFX: 高跟鞋落地 |
| 19 | 70-74s | 4s | Victor 指向 Clara 下令，安保围上；Ethan 揽住她的腰护到身侧，吊灯猛闪。叙事功能：冲突/异常 | Victor: "Grab her." / "抓住她。" | 跟拍中景 | Victor、安保、Clara、Ethan / 宴会厅 | SFX: 电流爆闪 |
| 20 | 74-77s | 3s | 宴会厅瞬间停电，暴雨砸向落地窗，闪电照亮 Victor 怒吼的脸。叙事功能：结果/紧迫感 | Victor: "Clara!" | 闪电明灭广角 | 宾客、Victor / 宴会厅 | SFX: 尖叫、暴雨、雷鸣 |
| 21 | 77-80s | 3s | 黑暗中 Ethan 低头看 Clara；她抱住他肩，他揽紧她转向侧门冲出。叙事功能：钩子/动作 | Ethan: "Hold on." / "抓紧。" | 跟拍双人中近景 | Ethan、Clara / 宴会厅侧门 | 末镜出逃方向明确 |
"""
TITLE = "ep2_wedding_showdown_80s"


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
    out_dir = repo_root / "comparison" / "output_ep2"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[ep2] storyboard length: {len(STORYBOARD)} chars", flush=True)
    print(f"[ep2] >>> calling generate_bgm_from_storyboard (GPT + Suno + post)...", flush=True)
    t0 = time.time()
    result = generate_bgm_from_storyboard(
        storyboard_text=STORYBOARD,
        title=TITLE,
        out_dir=out_dir,
        config=cfg,
    )
    result["elapsed_s"] = round(time.time() - t0, 1)

    analysis = result["analysis"]
    print(f"[ep2] GPT picked primary_tone={analysis['primary_tone']} "
          f"intensity={analysis['primary_intensity']} total={analysis['total_duration_s']}s "
          f"shots={len(analysis['shots'])} cues={len(analysis['cues'])}", flush=True)
    for c in analysis["cues"]:
        print(f"[ep2]   cue {c['id']} {c['start_s']}-{c['end_s']}s {c['tone']} "
              f"intensity_peak={c['intensity_peak']}: {c.get('narrative_summary','')[:60]}",
              flush=True)

    target_bpm = pick_bpm(analysis["primary_tone"], analysis["primary_intensity"])
    result["final_metrics"] = measure_final(Path(result["final_audio"]), target_bpm)
    print(f"[ep2] pipeline finished in {result['elapsed_s']}s", flush=True)
    print(f"[ep2] target_duration={result['target_duration_s']}s "
          f"final_duration={(result['final_duration_ms'] or 0)/1000:.3f}s "
          f"delta={result['duration_delta_ms']}ms", flush=True)
    print(f"[ep2] metrics={result['final_metrics']}", flush=True)
    print(f"[ep2] final={result['final_audio']}", flush=True)

    summary = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "script_title": TITLE,
        "target_bpm": target_bpm,
        "result": result,
    }
    (repo_root / "comparison" / "ep2_results.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("[ep2] DONE wrote comparison/ep2_results.json", flush=True)


if __name__ == "__main__":
    main()
