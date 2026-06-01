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
         "stinger_at": null}
    ]
}
"""
from __future__ import annotations
import json
import re
from typing import Optional

from .config import Config
from .http_util import SESSION
from .tone_params import TONE_PARAMS

ALLOWED_TONES = list(TONE_PARAMS.keys())

# Tone 近似映射表 - 用于修复GPT输出的未知情绪
TONE_FUZZY_MAP = {
    # 近似情绪映射
    "温暖": "温馨",
    "暖": "温馨",
    "感人": "温馨",
    "浪漫": "温馨",
    "爱": "温馨",
    "甜蜜": "温馨",
    "释然": "温馨",
    "放松": "温馨",
    "温和": "温馨",

    "胜利": "励志",
    "成功": "励志",
    "振奋": "励志",
    "希望": "励志",
    "鼓舞": "励志",
    "向上": "励志",
    "奋斗": "励志",

    "复仇": "反击",
    "报复": "反击",
    "逆袭": "反击",
    "反击": "反击",
    "压制": "反击",
    "还击": "反击",

    "压力": "豪门",
    "权势": "豪门",
    "等级": "豪门",
    "阶层": "豪门",
    "奢侈": "豪门",
    "富贵": "豪门",

    "安静": "静默",
    "沉默": "静默",
    "停顿": "静默",
    "静止": "静默",
    "屏息": "静默",

    "怪异": "异常",
    "诡异": "异常",
    "诡异": "异常",
    "不祥": "异常",
    "超自然": "异常",
    "灵异": "异常",

    "害怕": "恐惧",
    "惊恐": "恐惧",
    "恐怖": "恐惧",
    "惊骇": "恐惧",

    "神秘": "悬疑",
    "疑惑": "悬疑",
    "好奇": "悬疑",
    "不确定": "悬疑",
    "迷": "悬疑",

    "悲伤": "悲伤",
    "难过": "悲伤",
    "痛苦": "悲伤",
    "哀": "悲伤",
    "哭": "悲伤",

    "打斗": "动作",
    "打": "动作",
    "战斗": "动作",
    "追": "动作",
    "跑": "动作",
    "激烈": "动作",

    "紧张": "紧张",
    "急": "紧张",
    "紧迫": "紧张",
    "冲突": "紧张",
    "对峙": "紧张",
    "压力": "紧张",
    "危机": "紧张",
}

SYSTEM_PROMPT = (
    "You are a senior film score composer and music supervisor. "
    "You read short-drama scripts and decompose them into emotional timelines "
    "with hard music parameters. Only output valid JSON, no prose."
)


def _build_user_prompt(script_text: str, script_title: str) -> str:
    return f"""Analyze the following short-drama scene script and return a JSON object.

Title: {script_title}

Script:
{script_text}

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

IMPORTANT - Emotional transition detection:
- Watch for KEYWORDS indicating emotional shifts: "转暖" (warming), "胜利" (victory), "合作" (cooperation), "结婚" (marriage), "释然" (relief), "惊喜" (surprise), "真相大白" (truth revealed)
- When scenes contain positive/relief keywords after tension, use appropriate tones like:
  * "励志" for victory, cooperation, warming tone
  * "温馨" for romantic moments, marriage revelation
  * "豪门" for resolved power dynamics
- DO NOT default all scenes to "紧张" — capture the actual emotional arc
- The timeline should reflect REAL emotional changes, not just the dominant tone

IMPORTANT - Narrative node detection:
- Watch for KEYWORDS indicating narrative shifts that MUST create new timeline segments:
  * "反转" (reversal), "真相大白" (truth revealed), "胜利" (victory), "和解" (reconciliation)
  * "结婚" (marriage), "合作" (cooperation), "释然" (relief), "豁然开朗" (epiphany), "关键动作" (key action)
  * "惊喜" (surprise), "突变" (sudden change)
- These keywords indicate dramatic turning points that require separate music segments
- Each narrative node MUST start a new timeline segment with appropriate emotional_tone
- DO NOT merge scenes containing narrative nodes with previous segments

Respond with JSON only.
"""


def _smart_truncate(script_text: str, max_chars: int = 8000) -> str:
    """智能截断剧本，保留开头、中间高潮、结尾。

    策略：
    - 保留前40% (建立场景)
    - 保留后30% (结尾反转)
    - 中间按比例采样
    """
    if len(script_text) <= max_chars:
        return script_text

    # 计算各部分长度
    head_len = int(max_chars * 0.4)
    tail_len = int(max_chars * 0.3)
    middle_len = max_chars - head_len - tail_len

    head = script_text[:head_len]
    tail = script_text[-tail_len:]

    # 中间部分：取关键场景标记附近的内容
    middle = script_text[head_len:-tail_len]
    if len(middle) > middle_len:
        # 按场景分隔符分割，均匀采样
        scenes = re.split(r'\n\n+|第\d+场', middle)
        if len(scenes) > 1:
            # 保留首尾，中间均匀采样
            sampled = []
            current_len = 0
            for i, scene in enumerate(scenes):
                if i == 0 or i == len(scenes) - 1:
                    sampled.append(scene)
                    current_len += len(scene)
                elif current_len + len(scene) < middle_len:
                    sampled.append(scene)
                    current_len += len(scene)
            middle = '\n\n'.join(sampled)
        else:
            # 没有场景分隔，直接截断
            middle = middle[:middle_len]

    return head + middle + tail


def _validate_and_repair(data: dict, script_title: str, script_text: str) -> dict:
    """验证并修复GPT输出的JSON结构。

    检查：
    - primary_tone, primary_intensity, total_duration 存在
    - timeline 每条有完整字段
    - duration 总和等于 total_duration
    """
    # 1. 检查并修复顶层字段
    if "primary_tone" not in data or not data["primary_tone"]:
        data["primary_tone"] = "紧张"
    else:
        data["primary_tone"] = normalize_tone(data["primary_tone"])

    if "primary_intensity" not in data:
        data["primary_intensity"] = 5
    else:
        data["primary_intensity"] = _coerce_intensity(data["primary_intensity"])

    if "total_duration" not in data or not data["total_duration"]:
        data["total_duration"] = _extract_duration_fallback(script_text)
    else:
        data["total_duration"] = int(data["total_duration"])

    if "emotional_arc" not in data:
        data["emotional_arc"] = f"{script_title}的BGM配乐"
    if "tone_explanation" not in data:
        data["tone_explanation"] = ""

    # 2. 检查并修复 timeline
    if "timeline" not in data or not data["timeline"]:
        data["timeline"] = [{
            "time_range": f"0-{data['total_duration']}s",
            "duration": data["total_duration"],
            "scene_description": "全场景BGM",
            "emotional_tone": data["primary_tone"],
            "intensity": data["primary_intensity"],
            "stinger_at": None,
        }]
    else:
        # 修复每条timeline记录
        for i, seg in enumerate(data["timeline"]):
            # 检查必需字段
            if "time_range" not in seg:
                seg["time_range"] = f"{seg.get('start', 0)}-{seg.get('end', data['total_duration'])}s"

            if "duration" not in seg:
                # 从 time_range 解析 duration
                match = re.search(r'(\d+)-(\d+)', str(seg["time_range"]))
                if match:
                    seg["duration"] = int(match.group(2)) - int(match.group(1))
                else:
                    seg["duration"] = 10

            if "scene_description" not in seg or not seg["scene_description"]:
                seg["scene_description"] = f"场景{i+1}"

            if "emotional_tone" not in seg or not seg["emotional_tone"]:
                seg["emotional_tone"] = data["primary_tone"]
            else:
                seg["emotional_tone"] = normalize_tone(seg["emotional_tone"])

            if "intensity" not in seg:
                seg["intensity"] = data["primary_intensity"]
            else:
                seg["intensity"] = _coerce_intensity(seg["intensity"])

            if "stinger_at" not in seg:
                seg["stinger_at"] = None

        # 3. 校验 duration 总和
        total_from_timeline = sum(seg.get("duration", 0) for seg in data["timeline"])
        target_duration = data["total_duration"]

        if total_from_timeline != target_duration:
            # 尝试从 time_range 重新计算 duration
            for seg in data["timeline"]:
                match = re.search(r'(\d+)-(\d+)', str(seg.get("time_range", "")))
                if match:
                    seg["duration"] = int(match.group(2)) - int(match.group(1))

            total_from_timeline = sum(seg.get("duration", 0) for seg in data["timeline"])

            # 如果仍不一致，修正最后一段
            if total_from_timeline != target_duration:
                if data["timeline"]:
                    diff = target_duration - total_from_timeline
                    data["timeline"][-1]["duration"] += diff
                    # 更新 time_range
                    last_seg = data["timeline"][-1]
                    match = re.search(r'(\d+)-', str(last_seg["time_range"]))
                    if match:
                        start = int(match.group(1))
                        last_seg["time_range"] = f"{start}-{target_duration}s"

    return data


def analyze_script_structured(
    script_text: str,
    script_title: str,
    config: Optional[Config] = None,
) -> dict:
    cfg = config or Config()

    # 智能截断剧本
    truncated_script = _smart_truncate(script_text)

    payload = {
        "model": cfg.gpt_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(truncated_script, script_title)},
        ],
        "temperature": 0.2,  # 降低随机性，提高稳定性
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {cfg.gpt_api_key}",
        "Content-Type": "application/json",
    }

    # 第一次尝试
    try:
        r = SESSION.post(
            f"{cfg.gpt_api_base}/chat/completions",
            headers=headers, json=payload, timeout=90,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        return _validate_and_repair(data, script_title, script_text)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[gpt_analyzer] First attempt failed: {e}, retrying...")

        # Retry 一次
        try:
            r = SESSION.post(
                f"{cfg.gpt_api_base}/chat/completions",
                headers=headers, json=payload, timeout=90,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return _validate_and_repair(data, script_title, script_text)
        except Exception as e2:
            print(f"[gpt_analyzer] Second attempt failed: {e2}, entering repair mode")

            # Repair mode: 返回最小可用结构
            return {
                "primary_tone": "紧张",
                "primary_intensity": 5,
                "total_duration": _extract_duration_fallback(script_text),
                "emotional_arc": f"{script_title} - BGM",
                "tone_explanation": "自动生成",
                "timeline": [{
                    "time_range": f"0-{_extract_duration_fallback(script_text)}s",
                    "duration": _extract_duration_fallback(script_text),
                    "scene_description": "全场景BGM",
                    "emotional_tone": "紧张",
                    "intensity": 5,
                    "stinger_at": None,
                }]
            }


def normalize_tone(tone: Optional[str]) -> str:
    """统一的情绪规范化函数。

    优先级：
    1. 直接匹配允许列表
    2. 模糊映射表匹配
    3. 关键词匹配
    4. 默认"紧张"
    """
    if not tone:
        return "紧张"

    tone = tone.strip()

    # 1. 直接匹配
    if tone in ALLOWED_TONES:
        return tone

    # 2. 模糊映射表
    if tone in TONE_FUZZY_MAP:
        return TONE_FUZZY_MAP[tone]

    # 3. 关键词匹配
    for key, value in TONE_FUZZY_MAP.items():
        if key in tone or tone in key:
            return value

    # 4. 默认fallback
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
