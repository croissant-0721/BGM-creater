"""Suno prompt builder - 从BGM规划生成音乐化的Suno提示词。

目标：
- 将剧情描述转换为音乐语言
- 统一 tone → Suno descriptor 映射
- 强制输出 instrumental
- 控制prompt长度
"""
from __future__ import annotations
from typing import List, Dict, Optional

# Tone → Suno 音乐描述符映射
TONE_TO_SUNO_DESCRIPTOR = {
    "紧张": {
        "style": "cinematic suspense, tense underscore, dramatic tension",
        "instruments": "ostinato strings, low drone, ticking percussion, pulsing bass",
        "energy": "driving, high tension, relentless",
        "production": "Hans Zimmer style, hybrid orchestral",
    },
    "悬疑": {
        "style": "cinematic mystery, ambient tension, psychological underscore",
        "instruments": "dissonant pad, prepared piano, low drone, sparse glockenspiel",
        "energy": "subtle, minimal, restrained",
        "production": "Trent Reznor / Mica Levi style, sound design forward",
    },
    "温馨": {
        "style": "cinematic warm, emotional piano, tender underscore",
        "instruments": "felt piano, warm strings, soft pads, wooden percussion",
        "energy": "gentle, soft, intimate",
        "production": "Ludovico Einaudi / Joe Hisaishi style",
    },
    "悲伤": {
        "style": "cinematic melancholic, emotional underscore, somber",
        "instruments": "solo cello, solo piano, long reverb tail, sparse strings",
        "energy": "restrained, minimal, soft",
        "production": "Max Richter / Johann Johannsson style, minimalist",
    },
    "恐惧": {
        "style": "horror score, dread, ominous atmosphere",
        "instruments": "low drone, irregular percussion, reversed piano, wind texture",
        "energy": "restrained but menacing",
        "production": "Mica Levi (Under the Skin) style, abstract horror",
    },
    "动作": {
        "style": "cinematic action, driving underscore, aggressive percussion",
        "instruments": "hybrid orchestral, electronic drums, brass stabs, taiko",
        "energy": "explosive, climactic, driving",
        "production": "Lorne Balfe / Brian Tyler style, propulsive",
    },
    "励志": {
        "style": "cinematic uplifting, inspirational orchestral, hopeful rise",
        "instruments": "rising strings, french horns, anthemic swell, soft choir-like pad",
        "energy": "building, swelling, triumphant",
        "production": "Steve Jablonsky / Two Steps From Hell style",
    },
    "羞辱": {
        "style": "cinematic tense, oppressive underscore, social pressure",
        "instruments": "sub bass pulse, muted tight strings, low piano clusters",
        "energy": "steady but suffocating",
        "production": "K-drama OST antagonist cue, taut and oppressive",
    },
    "静默": {
        "style": "cinematic silence, minimal tension, held breath",
        "instruments": "near silence, very low drone, single piano notes, ultra-soft pad",
        "energy": "minimal, restrained",
        "production": "held-breath moment, ultra minimalist",
    },
    "反击": {
        "style": "trap orchestral, revenge underscore, satisfying buildup",
        "instruments": "driving strings ostinato, trap-orchestral hybrid, brass stabs, taiko",
        "energy": "aggressive, driving, explosive",
        "production": "K-drama montage flavor, trap-orchestral revenge cue",
    },
    "豪门": {
        "style": "cinematic refined, luxury drama, elegant underscore",
        "instruments": "legato strings, piano, french horn, soft sub bass",
        "energy": "steady, refined, cold",
        "production": "upper-class corporate drama, refined and cold",
    },
    "异常": {
        "style": "psychological unease, eerie texture, anomalous atmosphere",
        "instruments": "reversed strings, very low drone, metallic shimmer, wide reverb pad",
        "energy": "unsettling, restrained",
        "production": "supernatural intrusion, sound-design hybrid",
    },
}

# Intensity → Musical energy 映射
INTENSITY_TO_ENERGY = {
    (1, 3): {
        "adjective": "restrained, minimal",
        "dynamic": "soft, subtle",
        "verbs": "whisper, hint at",
    },
    (4, 6): {
        "adjective": "steady pulse, moderate tension",
        "dynamic": "medium, building",
        "verbs": "build, suggest",
    },
    (7, 8): {
        "adjective": "driving, high tension",
        "dynamic": "loud, intense",
        "verbs": "drive, push",
    },
    (9, 10): {
        "adjective": "explosive, climactic, aggressive",
        "dynamic": "full, powerful",
        "verbs": "explode, climax",
    },
}

# Transition → Suno prompt 映射
TRANSITION_TO_PROMPT = {
    "cold": "abrupt opening, immediate impact",
    "swell": "gradual build, slow crescendo",
    "hit": "impact accent, sharp attack",
    "drop": "sudden breakdown, drop out",
}

# 统一的 negative prompt
NEGATIVE_PROMPT = (
    "vocals, lyrics, dialogue, voice, voiceover, "
    "thunder, explosion, gunshot, scream, sound effects, foley, "
    "diegetic sounds, crowd noise, traffic, weather sounds"
)


def build_suno_prompts(
    bg_plan: dict,
    target_duration_s: Optional[int] = None,
) -> List[dict]:
    """从BGM规划构建Suno提示词列表。

    Args:
        bg_plan: 从 analyze_storyboard 返回的BGM规划
        target_duration_s: 目标总时长（可选）

    Returns:
        提示词列表，每个cue一个
    """
    cues = bg_plan.get("cues", [])
    if not cues:
        return []

    target_duration = target_duration_s or bg_plan.get("total_duration_s", 60)

    results = []
    for cue in cues:
        prompt_data = _build_single_prompt(cue, bg_plan)
        results.append(prompt_data)

    return results


def _build_single_prompt(cue: dict, bg_plan: dict) -> dict:
    """为单个cue构建Suno提示词。"""
    tone = cue.get("tone", "紧张")
    intensity = cue.get("intensity_peak", 5)
    duration = cue["end_s"] - cue["start_s"]
    transition_in = cue.get("transition_in", "swell")
    transition_out = cue.get("transition_out", "swell")

    # 获取tone对应的音乐描述
    tone_desc = TONE_TO_SUNO_DESCRIPTOR.get(tone, TONE_TO_SUNO_DESCRIPTOR["紧张"])

    # 获取intensity对应的能量描述
    energy_desc = _get_energy_description(intensity)

    # 构建prompt
    prompt = _format_prompt(
        tone=tone,
        tone_desc=tone_desc,
        energy_desc=energy_desc,
        duration_s=duration,
        transition_in=transition_in,
        transition_out=transition_out,
        narrative=cue.get("narrative_summary", ""),
    )

    # 构建tags
    tags = _build_tags(tone, tone_desc, intensity)

    return {
        "cue_id": cue["id"],
        "start_s": cue["start_s"],
        "end_s": cue["end_s"],
        "duration_s": duration,
        "tone": tone,
        "intensity": intensity,
        "suno_prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "tags": tags,
        "transition_in": transition_in,
        "transition_out": transition_out,
    }


def _get_energy_description(intensity: int) -> dict:
    """根据强度获取能量描述。"""
    intensity = max(1, min(10, intensity))

    for (low, high), desc in INTENSITY_TO_ENERGY.items():
        if low <= intensity <= high:
            return desc

    return INTENSITY_TO_ENERGY[(4, 6)]


def _format_prompt(
    tone: str,
    tone_desc: dict,
    energy_desc: dict,
    duration_s: int,
    transition_in: str,
    transition_out: str,
    narrative: str,
) -> str:
    """格式化Suno prompt。

    结构：
    1. Header: 无人声标记
    2. 基础描述: 风格 + 乐器
    3. 动态描述: 强度 + 过渡
    4. Footer: 无人声强化
    """
    # Header
    header = "[INSTRUMENTAL ONLY - NO VOCALS - PURE SCORE]"

    # 基础描述
    base = (
        f"A {tone_desc['style']} cue.\n"
        f"Core instrumentation: {tone_desc['instruments']}.\n"
        f"Production style: {tone_desc['production']}."
    )

    # 动态描述
    transition_in_prompt = TRANSITION_TO_PROMPT.get(transition_in, "gradual build")
    transition_out_prompt = TRANSITION_TO_PROMPT.get(transition_out, "gradual build")

    dynamic = (
        f"Energy: {energy_desc['adjective']}, {energy_desc['dynamic']}.\n"
        f"Entry: {transition_in_prompt}.\n"
        f"Exit: {transition_out_prompt}.\n"
        f"Duration: ~{duration_s}s."
    )

    # Footer - 多重无人声防护
    footer = (
        "\nCRITICAL: NO VOCALS ALLOWED.\n"
        "- NO singing, NO lyrics, NO vocal chops, NO vocal samples\n"
        "- NO voice, NO choir, NO humming, NO vocal pads\n"
        "- NO ad-libs, NO vocal FX, NO pitch-shifted vocals\n"
        "- Pure orchestral/instrumental score only\n"
        "- All sounds must be synthesized or acoustic instruments ONLY"
    )

    prompt = f"{header}\n\n{base}\n\n{dynamic}{footer}"

    # 长度控制：120-220字符
    prompt = _truncate_prompt(prompt, min_len=120, max_len=220)

    return prompt


def _build_tags(tone: str, tone_desc: dict, intensity: int) -> str:
    """构建Suno tags。

    格式: style, instruments, key characteristics, instrumental only
    """
    style = tone_desc["style"].split(",")[0].strip()
    instruments = ", ".join(tone_desc["instruments"].split(",")[:3])

    tags = f"{style}, {instruments}, cinematic underscore, instrumental only, no vocals"

    # 长度控制：<= 120字符
    if len(tags) > 120:
        tags = tags[:117] + "..."

    return tags


def _truncate_prompt(prompt: str, min_len: int, max_len: int) -> str:
    """智能截断prompt到目标长度。

    策略：
    - 优先保留header和footer
    - 截断中间的动态描述
    """
    if min_len <= len(prompt) <= max_len:
        return prompt

    if len(prompt) > max_len:
        # 找到第二个\n\n（header和base之后）
        parts = prompt.split("\n\n")
        if len(parts) >= 3:
            # 保留header和footer，截断dynamic
            header = parts[0]
            base = parts[1]
            footer = parts[-1]

            # 计算可用长度
            available = max_len - len(header) - len(footer) - 10  # 留一些buffer
            base = base[:available]

            prompt = f"{header}\n\n{base}\n\n{footer}"

    return prompt


def build_unified_prompt(
    bg_plan: dict,
    target_duration_s: Optional[int] = None,
) -> dict:
    """构建单个统一的Suno提示词（用于单次生成全片BGM）。

    这是 render_storyboard_payload 的音乐化版本。
    """
    cues = bg_plan.get("cues", [])
    if not cues:
        return {}

    primary_tone = bg_plan.get("primary_tone", "紧张")
    primary_intensity = bg_plan.get("primary_intensity", 5)
    total_duration = target_duration_s or bg_plan.get("total_duration_s", 60)

    # 获取主基调的描述
    tone_desc = TONE_TO_SUNO_DESCRIPTOR.get(primary_tone, TONE_TO_SUNO_DESCRIPTOR["紧张"])

    # 构建多情绪的动态弧线
    arc_lines = []
    for cue in cues:
        cue_tone = cue.get("tone", primary_tone)
        cue_intensity = cue.get("intensity_peak", 5)
        cue_desc = TONE_TO_SUNO_DESCRIPTOR.get(cue_tone, tone_desc)

        arc_lines.append(
            f"- {cue['start_s']}-{cue['end_s']}s: {cue_desc['style']}, "
            f"intensity {cue_intensity}/10, "
            f"emphasis on {cue_desc['instruments'].split(',')[0].strip()}"
        )

    arc_block = "\n".join(arc_lines)

    # Header
    header = "[INSTRUMENTAL ONLY - NO VOCALS - PURE SCORE]"

    # 基础描述
    base = (
        f"A {tone_desc['style']}-anchored cinematic cue, "
        f"total length ~{total_duration}s.\n"
        f"Core instrumentation: {tone_desc['instruments']}.\n"
        f"Production style: {tone_desc['production']}."
    )

    # 动态弧线
    dynamic = f"Follow this emotional arc, transitioning smoothly:\n{arc_block}"

    # Footer
    footer = (
        "\n\nCRITICAL: NO VOCALS ALLOWED.\n"
        "- NO singing, NO lyrics, NO vocal chops, NO vocal samples\n"
        "- NO voice, NO choir, NO humming, NO vocal pads\n"
        "- Pure orchestral/instrumental score only"
    )

    prompt = f"{header}\n\n{base}\n\n{dynamic}{footer}"

    # 长度控制
    prompt = _truncate_prompt(prompt, min_len=150, max_len=300)

    # Tags
    tags = _build_tags(primary_tone, tone_desc, primary_intensity)

    return {
        "prompt": prompt,
        "tags": tags,
        "title": bg_plan.get("title", "BGM"),
        "mv": "chirp-v4",
        "make_instrumental": True,
    }
