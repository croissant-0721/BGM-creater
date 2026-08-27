"""Test multi-segment BGM generation with auto-stitching.

测试案例：前紧张后温馨的场景
"""
import sys
sys.path.insert(0, r'd:\1 a universe\BGM-creater')

from pathlib import Path
from bgm_v2 import generate_bgm_multisegment, detect_emotional_cues
from bgm_v2.config import Config

# 测试案例：前紧张后温馨
TEST_ANALYSIS = {
    "title": "Tension_to_Warm_Test",
    "primary_tone": "紧张",
    "primary_intensity": 7,
    "total_duration": 52,
    "emotional_arc": "前28秒紧张铺垫，后24秒温馨释然",
    "timeline": [
        {
            "time_range": "0-28s",
            "duration": 28,
            "scene_description": "紧张对峙场景",
            "emotional_tone": "紧张",
            "intensity": 8,
            "stinger_at": None,
        },
        {
            "time_range": "28-52s",
            "duration": 24,
            "scene_description": "误会解除，温馨释然",
            "emotional_tone": "温馨",
            "intensity": 6,
            "stinger_at": None,
        },
    ],
}


def main():
    cfg = Config()
    out_dir = Path(r"d:\1 a universe\BGM-creater\output\multisegment_test")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("MULTI-SEGMENT BGM GENERATION TEST")
    print("=" * 80)
    print(f"\n场景: {TEST_ANALYSIS['emotional_arc']}")
    print(f"总时长: {TEST_ANALYSIS['total_duration']}s")
    print()

    # 检测cues
    cues = detect_emotional_cues(TEST_ANALYSIS)
    print("检测到的情绪分段:")
    for cue in cues:
        print(f"  Cue {cue['id']}: {cue['start_s']}-{cue['end_s']}s | {cue['tone']} | 强度{cue['intensity_peak']}/10")

    print()
    print("=" * 80)
    print("开始生成（每段独立生成Suno音频，然后自动拼接）...")
    print("=" * 80)

    # 生成
    result = generate_bgm_multisegment(
        analysis=TEST_ANALYSIS,
        title="Test_Tension_Warm",
        out_dir=out_dir,
        config=cfg,
    )

    print()
    print("=" * 80)
    print("生成完成!")
    print("=" * 80)
    print(f"\n分段文件:")
    for seg in result.get("segments", []):
        print(f"  Cue {seg['cue_id']}: {seg['audio']}")

    print(f"\n最终完整BGM: {result['final_audio']}")
    print(f"总时长: {result['total_duration_s']}s")


if __name__ == "__main__":
    main()
