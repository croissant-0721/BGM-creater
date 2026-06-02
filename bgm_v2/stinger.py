"""Stinger 合成 + 卡点放置。

在连续 BGM 床上，于剧情高潮/反转的精确时间点叠加短促音乐重音(stinger)，
让配乐"砸在点上"。stinger 程序化合成（免费、精确、可调），不依赖外部素材。

- impact: 低频砸下（boom + 瞬态），用于冲突爆发/泼酒/反转那一下
- riser:  前导渐强扫频，铺在 impact 前 ~1.4s，把情绪推上去
- sub_drop: 低频下坠，用于情绪释然/转场

放置点从分析里的细粒度节拍(cues/timeline)挑：强度爬升到高位、或命中叙事节点。
"""
from __future__ import annotations
from typing import List, Optional
import numpy as np
from pydub import AudioSegment

# 叙事节点（与 multisegment_pipeline 保持一致，触发硬重音）
_NODES = [
    "反转", "真相", "泼酒", "羞辱", "胜利", "和解", "结婚", "突变",
    "指控", "甩出", "逼问", "警告", "出手", "冻结", "钉住",
]

# 叙事功能里属于"该砸点"的节拍
_PUNCH_FUNCS = {"反转", "转折", "关键动作", "结果", "钩子", "反击"}
# 情绪族 → 决定 stinger 种类
_OMINOUS_TONES = {"悬疑", "异常", "恐惧"}   # 用 sub_drop 低频下坠（阴森）
_WARM_TONES = {"温馨", "励志"}             # 柔情段不砸重音

_SR = 44100


def _to_segment(sig: np.ndarray, sr: int = _SR) -> AudioSegment:
    """float[-1,1] 单声道 → 16bit 立体声 AudioSegment。"""
    sig = np.clip(sig, -1.0, 1.0)
    arr = (sig * 32767).astype(np.int16)
    stereo = np.repeat(arr[:, None], 2, axis=1).flatten()
    return AudioSegment(stereo.tobytes(), frame_rate=sr, sample_width=2, channels=2)


def synth_impact(duration_ms: int = 1100, sr: int = _SR, seed: int = 0) -> AudioSegment:
    """低频砸下：50/75Hz 正弦 + 瞬态噪声，指数衰减。"""
    rng = np.random.RandomState(seed)
    n = int(sr * duration_ms / 1000)
    t = np.arange(n) / sr
    env = np.exp(-t * 5.0)
    boom = (np.sin(2 * np.pi * 50 * t) + 0.45 * np.sin(2 * np.pi * 75 * t)) * env
    click = rng.randn(n) * np.exp(-t * 38.0) * 0.35          # 起始瞬态"咚"
    sig = boom * 0.92 + click
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.9
    return _to_segment(sig, sr).fade_out(120)


def synth_riser(duration_ms: int = 1400, sr: int = _SR, seed: int = 1) -> AudioSegment:
    """前导渐强扫频：噪声+上行音，体积加速爬升，结束在重音点。"""
    rng = np.random.RandomState(seed)
    n = int(sr * duration_ms / 1000)
    t = np.arange(n) / sr
    dur = duration_ms / 1000
    env = (t / dur) ** 2.5                                   # 加速渐强
    freqs = 160 + 1700 * (t / dur)                           # 上行扫频
    phase = 2 * np.pi * np.cumsum(freqs) / sr
    tone = np.sin(phase)
    noise = rng.randn(n)
    sig = (0.55 * noise + 0.45 * tone) * env
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.8
    return _to_segment(sig, sr).fade_in(80)


def synth_sub_drop(duration_ms: int = 1300, sr: int = _SR, seed: int = 2) -> AudioSegment:
    """低频下坠：频率从 120Hz 滑到 35Hz，用于释然/转场。"""
    n = int(sr * duration_ms / 1000)
    t = np.arange(n) / sr
    dur = duration_ms / 1000
    freqs = 120 * (35 / 120) ** (t / dur)
    phase = 2 * np.pi * np.cumsum(freqs) / sr
    env = np.exp(-t * 2.2)
    sig = np.sin(phase) * env
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * 0.85
    return _to_segment(sig, sr).fade_out(150)


def _extract_beats(analysis: dict) -> List[dict]:
    """取细粒度节拍 (ts, intensity, tone, funcs, text)。

    优先用逐镜 shots（最细，能抓到 montage 每一记），其次 cues，再次 timeline。
    """
    beats = []
    if analysis.get("shots"):
        for s in analysis["shots"]:
            beats.append({
                "ts": s.get("start_s", 0),
                "intensity": s.get("intensity", 5),
                "tone": s.get("tone", ""),
                "funcs": set(s.get("narrative_func", []) or []),
                "text": s.get("summary_zh", ""),
            })
    elif analysis.get("cues"):
        for c in analysis["cues"]:
            beats.append({
                "ts": c.get("start_s", 0),
                "intensity": c.get("intensity_peak", c.get("intensity", 5)),
                "tone": c.get("tone", ""),
                "funcs": set(),
                "text": c.get("narrative_summary", "") or c.get("tone", ""),
            })
    elif analysis.get("timeline"):
        cursor = 0
        for seg in analysis["timeline"]:
            beats.append({
                "ts": cursor,
                "intensity": seg.get("intensity", 5),
                "tone": seg.get("emotional_tone", ""),
                "funcs": set(),
                "text": seg.get("scene_description", ""),
            })
            cursor += seg.get("duration", 0)
    return beats


def plan_stingers(
    analysis: dict,
    total_s: int,
    *,
    min_gap_s: float = 4.0,
    max_count: int = 6,
    min_intensity: int = 7,
) -> List[dict]:
    """镜头级 + 分情绪挑卡点。

    规则：
    - 候选 = 该镜叙事功能命中 {反转/转折/关键动作/结果/钩子/反击} 或文本含节点词，
      且强度 >= min_intensity。
    - 种类按情绪族：悬疑/异常/恐惧 → sub_drop（阴森低频）；温馨/励志 → 不砸；
      其余（紧张/反击/羞辱/悲伤/静默…）→ impact，高强度(>=8)前加 riser。
    - min_gap_s 控制密度（montage 默认 4s 一记，正好踩在每条通知上）。
    Returns list of {ts_ms, kind, gain_db}，按时间排序。
    """
    beats = _extract_beats(analysis)
    plan: List[dict] = []
    last_ts = -10_000

    for b in beats:
        ts, inten, tone = b["ts"], b["intensity"], b.get("tone", "")
        funcs, text = b.get("funcs", set()), b.get("text", "")

        is_beat = bool(funcs & _PUNCH_FUNCS) or any(k in (text or "") for k in _NODES)
        if not is_beat or inten < min_intensity:
            continue
        if tone in _WARM_TONES:          # 温馨/励志：柔情不砸重音
            continue
        if ts >= total_s - 1 or ts * 1000 - last_ts < min_gap_s * 1000:
            continue

        kind = "sub_drop" if tone in _OMINOUS_TONES else "impact"
        gain = -9 if (kind == "impact" and inten >= 8) else -12
        if kind == "impact" and inten >= 8 and ts >= 2:
            plan.append({"ts_ms": int(ts * 1000 - 1400), "kind": "riser", "gain_db": -15})
        plan.append({"ts_ms": int(ts * 1000), "kind": kind, "gain_db": gain})
        last_ts = ts * 1000

    # 截断到上限（保留最早的几处核心重音及其 riser）
    cores = [p for p in plan if p["kind"] != "riser"][:max_count]
    keep = {p["ts_ms"] for p in cores}
    plan = [p for p in plan
            if (p["kind"] != "riser" and p["ts_ms"] in keep)
            or (p["kind"] == "riser" and (p["ts_ms"] + 1400) in keep)]
    plan.sort(key=lambda p: p["ts_ms"])
    return plan


_SYNTH = {"impact": synth_impact, "riser": synth_riser, "sub_drop": synth_sub_drop}


def apply_stingers(bed: AudioSegment, plan: List[dict]) -> AudioSegment:
    """把 stinger 叠加到 bed 上（mix，不替换），精确对齐到时间点。"""
    out = bed
    for i, p in enumerate(plan):
        synth = _SYNTH.get(p["kind"])
        if not synth:
            continue
        s = synth(seed=i)               # 不同 seed 让多记重音不完全雷同
        s = s.apply_gain(p.get("gain_db", -9))
        pos = max(0, min(p["ts_ms"], len(out) - 1))
        out = out.overlay(s, position=pos)
    return out
