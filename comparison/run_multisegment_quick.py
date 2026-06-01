"""Quick test multi-segment BGM (shorter duration)."""
import sys
sys.path.insert(0, r'd:\1 a universe\BGM-creater')

from pathlib import Path
from bgm_v2 import generate_bgm_multisegment, detect_emotional_cues
from bgm_v2.config import Config

# 测试案例：前紧张后温馨（每段10秒）
TEST_ANALYSIS = {
    "title": "Quick_Tension_Warm",
    "primary_tone": "紧张",
    "primary_intensity": 7,
    "total_duration": 20,  # 更短的时长
    "emotional_arc": "前10秒紧张，后10秒温馨",
    "timeline": [
        {
            "time_range": "0-10s",
            "duration": 10,
            "scene_description": "紧张对峙",
            "emotional_tone": "紧张",
            "intensity": 8,
            "stinger_at": None,
        },
        {
            "time_range": "10-20s",
            "duration": 10,
            "scene_description": "温馨释然",
            "emotional_tone": "温馨",
            "intensity": 6,
            "stinger_at": None,
        },
    ],
}


def main():
    cfg = Config()
    out_dir = Path(r"d:\1 a universe\BGM-creater\output\quick_test")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("QUICK MULTI-SEGMENT TEST (20s total)")
    print("=" * 80)

    # 检测cues
    cues = detect_emotional_cues(TEST_ANALYSIS)
    print(f"\n检测到 {len(cues)} 个分段:")
    for cue in cues:
        print(f"  Cue {cue['id']}: {cue['start_s']}-{cue['end_s']}s | {cue['tone']}")

    print("\n开始生成...")
    result = generate_bgm_multisegment(
        analysis=TEST_ANALYSIS,
        title="QuickTest",
        out_dir=out_dir,
        config=cfg,
    )

    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)
    print(f"最终BGM: {result['final_audio']}")


if __name__ == "__main__":
    main()
