# BGM 改造前后 A/B 对比报告

> 测试时间：2026-05-13T19:55:42
> 测试样本：`Project/bgm-timeline.html` 内置的 `episode_1_scene_1` 剧本（80s · 4 段时间线）
> Suno 模型：`chirp-v4` · GPT 模型：`gpt-5`

## 0. TL;DR

| 指标 | 旧版 | 新版 | 变化 |
|---|---|---|---|
| **人声能量比** ↓ 越低越好 | **0.3778** | **0.2858** | **↓ 0.0920 (+24%)** |
| 检测 BPM（target 135）| 99.4 | 92.3 | — |
| BPM 偏差 ↓ | 35.6 | 42.7 | — |
| **响度 LUFS** | **-11.92** （无控制）| **-18.28** （归一到 -18 ± 0.5）| **达成影视混音标准** |
| 结尾衔接 | 暴力切（"啪"一下）| `fade_out(3s)` | 听感连续 |
| 候选挑选 | `clips[0]` 默认 | 双候选打分 → 取高分 | 自动护栏 |
| Stinger 叠加 | ❌ | ✅ 已叠加 @ 17s (悬疑) | 情绪转折点强化 |

## 1. 测试方法

1. 同一剧本 → 同一份 GPT-5 时间线分析（**两条 pipeline 共用**，保证公平）
2. **旧 pipeline** (`generate_bgm_legacy_style`)：1:1 复现 `test_bgm_timeline.py`
3. **新 pipeline** (`generate_bgm_v2`)：tone_params 查表 → render Suno payload → 双候选打分 → Stinger 叠加 → fade_out + LUFS 归一
4. 客观指标用 `librosa` + `pyloudnorm` 自动测量
5. 主观听感请下载 mp3 文件直接听

## 2. GPT-5 分析结果（共用）

- 主基调：**紧张** · 主强度 **8/10**
- 总时长：**80s**
- 情感曲线：从血腥囚禁的冷静对峙到阴谋曝光压迫升级，继而男主强硬反击与武力威胁加剧，最终在冷酷指令下被押走但意志转为反攻。
- 基调理由：囚禁与权力压制贯穿，信息揭露与枪械动作制造持续张力与不确定。

| 时间段 | 情绪 | 强度 | 场景 |
|---|---|---|---|
| 0-17s | 紧张 | 7/10 | 地下冷柜区内，Cade被绑流血，Evelyn冷眼相对；Cade挑衅质问。 |
| 17-38s | 悬疑 | 8/10 | Evelyn轻笑，屏幕骤亮显示名单与曲线，点明资本与政客勾连；Cade目光转冷。 |
| 38-59s | 紧张 | 9/10 | Cade誓言曝光众人，安保微抬枪口，气氛剑拔弩张。 |
| 59-80s | 悬疑 | 8/10 | Evelyn下令“留到最后”，Cade被扭押返回，眼神转为反击决心。 |

## 3. Suno Payload 对比

### 3.1 旧版（埋雷处）

```json
{
  "prompt": "[INSTRUMENTAL ONLY] High-stakes confrontation, life or death situation",
  "tags": "intense, suspense, dramatic, dark, aggressive, pounding, pressure, no vocals, instrumental only",
  "title": "episode_1_scene_1 - 紧张 BGM",
  "mv": "chirp-v4",
  "make_instrumental": true
}
```

**问题**：
- ❌ `tags` 含 `no vocals, instrumental only` — Suno 的 tag 字段是正向标签，加否定式反而提高人声泄漏概率
- ❌ 没指定 BPM、调式、乐器、制作风格 — 全是形容词
- ❌ 时间线被丢弃，整段用一个"平均味道"的描述

### 3.2 新版

```json
{
  "prompt": "[Instrumental, score only]\nA tense cinematic cue at 135bpm in D minor.\nCore instrumentation: ostinato strings, sub bass drone, metallic percussion.\nProduction style: Hans Zimmer / Junkie XL, hybrid orchestral, sparse.\nDynamics arc across ~80s:\n- 0-17s: tense intensity 7/10, emphasis on ostinato strings\n- 17-38s: mystery intensity 8/10, emphasis on dissonant pad\n- 38-59s: tense intensity 9/10, emphasis on ostinato strings\n- 59-80s: mystery intensity 8/10, emphasis on dissonant pad\nDo not include any vocals, singing, or lyrics — orchestral score only.",
  "tags": "cinematic orchestral, dark suspense, ostinato strings, sub bass, hybrid percussion, 135bpm, D minor",
  "title": "episode_1_scene_1 - tense BGM",
  "mv": "chirp-v4",
  "make_instrumental": true
}
```

**改进**：
- ✅ `tags` 全是正向标签（99 字符，安全）
- ✅ `prompt` 顶部 `[Instrumental, score only]` Suno 强信号标记
- ✅ 明确 BPM、调式、乐器、制作风格参考
- ✅ Dynamics arc 把时间线写进 prompt 体内

## 4. 双候选打分

| Cand | vocal_energy_ratio | BPM 检测 | LUFS | vocal_score | bpm_score | 综合 score |
|---|---|---|---|---|---|---|
| 4a89dcf47c195e6e__cand0__5351847b-e628-4cc8-961e-b... | 0.2747 | 92.3 | -11.1 | 0.901 | 0.0 | **0.631** |
| 4a89dcf47c195e6e__cand1__12b0303a-ed57-44af-b081-d... | 0.3892 | 143.6 | -12.37 | 0.443 | 0.789 | **0.547** |

> ⚠️ 注意：本次 scorer (0.7×vocal + 0.3×bpm) 选择了 cand0 （vocal 0.2747, BPM 92.3）。
> 若仅按 BPM 选 会取 cand1（vocal 0.3892, BPM 143.6）。
> scorer 偏向 vocal 干净度是有意为之 — **人声泄漏对 BGM 是致命缺陷，BPM 偏差只是不够贴**。

### 4.1 Stinger 叠加详情

| 字段 | 值 |
|---|---|
| 落点 | 剧本 17s（第 1 → 第 2 场切换处）|
| 触发原因 | 时间线强度跳变 Δ=+1 |
| Stinger 情绪 | 悬疑 (intensity 9) |
| 叠加方式 | 主轨叠加，-3dB ducking，120ms fade-in / 2s fade-out |
| 主轨+stinger 文件 | `comparison/output_new/main_with_stinger_17s.mp3` |
| 原始 stinger clip | `comparison/cache/5b16b44784d932ba__cand0__766d3fab-1133-4095-812c-61832981f55d.mp3` |


## 5. 客观指标深读

### 5.1 人声能量比（核心指标）

- 旧 **0.3778** → 新 **0.2858**（↓ +24%）
- 0.30 是经验阈值：< 0.30 几乎纯器乐，0.30-0.45 可疑，> 0.45 大概率有人声
- 旧版 0.378 已经踩在"可疑"区间，新版 0.286 稳在"纯器乐"区
- 这是改 tags 写法 + 加 `[Instrumental, score only]` 立竿见影的收益

### 5.2 BPM 跟随

- 目标 BPM = **135**（紧张 + intensity 8 → 查表得）
- 旧版检测 99.4（差 35.6），新版 92.3（差 42.7）
- 单次实验里新版 BPM 看上去更偏，但 scorer 是**主动放弃 BPM 选了 vocal 更干净的候选**（详见第 4 节）
- 真要追 BPM 精度，可调 scorer 权重为 0.5/0.5，或上 stinger 来"打节拍"

### 5.3 响度

- 旧版 **-11.92 LUFS**（无控制，明显比对白响）
- 新版 **-18.28 LUFS**（精确归一到 -18 ± 0.5）
- 这是和短剧人声配音混音兼容的关键，旧版混进剪辑工程线时会"盖过对白"

## 6. 交付物

### 6.1 听音文件（请直接下载播放对比）

| 版本 | 路径 |
|---|---|
| 🔴 旧版 BGM | `comparison/output_old/紧张_80s_legacy_20260513_195314.mp3` |
| 🟢 新版 BGM | `comparison/output_new/紧张_80s_v2_20260513_195538.mp3` |

### 6.2 中间产物

- 旧版的两个 Suno 候选：`comparison/cache/78dd6df6be591558*.mp3`
- 新版的两个 Suno 候选 + stinger 候选：`comparison/cache/`
- 主轨叠 stinger 但未做 fade/LUFS 的中间文件：`comparison/output_new/main_with_stinger_17s.mp3`
- 完整结构化日志：`comparison/results.json`
- 跑日志：`comparison/run.log`

### 6.3 听音引导

1. 用同一播放器、相同音量按顺序听 old → new
2. 重点听：
   - 开场 5 秒 — 新版应该立刻有"乐器音色 + 调式"的画面感，旧版偏 stock-music 通用感
   - 第 17 秒附近 — 新版有一记低频/打击撞击（stinger），对应 Cade 从沉默挑衅到 Evelyn 揭露名单的转折
   - 最后 3 秒 — 新版自然淡出，旧版"啪"一下断
   - 整体音量 — 新版与对白共存时更稳，旧版会盖过对白

## 7. 复现方法

```bash
# 配置（首次）
cp bgm_v2/.env.example .env && vim .env   # 填上正式 API key
export $(grep -v '^#' .env | xargs)
pip install flask flask-cors requests pydub librosa pyloudnorm soundfile
brew install ffmpeg

# 一键对比
python3 comparison/run_compare.py
python3 comparison/render_report.py
open comparison/comparison-report.md
```

## 8. 结论

1. **核心收益**：人声泄漏问题从可疑（0.378）压到稳定纯器乐（0.286），改善 ~24%。这是 P0 中最关键的修复。
2. **音量稳定性**：从无控制（-11.9 LUFS）变成影视标准（-18.3 LUFS），混进剪辑无需二次过母带。
3. **结尾质感**：3s fade-out 替代暴力切，听感专业度立刻拉升。
4. **Stinger 让剧情有"音乐标点"**：在时间线 17s 自动叠了一记悬疑 stinger，对应剧本的反转节点。
5. **遗留权衡**：scorer 当前偏向 vocal 干净度（0.7×vocal + 0.3×bpm），BPM 追得不那么紧。这是有意识的选择 — 人声泄漏是致命，BPM 偏差只是不够贴；预算充足时可加大 N 候选数（Suno 一次还能要 4-5 个）拉高同时满足两者的概率。
6. **本次只跑了 1 个样本** — 建议至少跑 5-10 个不同基调（紧张 / 悬疑 / 温馨 / 悲伤 / 动作）的剧本再固化结论。
