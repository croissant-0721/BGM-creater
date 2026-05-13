# 盼趣 AI · BGM 模块分析与优化方案

---

## 目录

1. [项目通俗讲解](#一项目通俗讲解)
2. [现状梳理](#二现状梳理代码层面)
3. [核心问题诊断](#三核心问题诊断)
4. [优化方案（按性价比排序）](#四优化方案按性价比排序)
5. [音乐学参数查表](#五音乐学参数查表必背)
6. [推荐落地路线图](#六推荐落地路线图)
7. [附录：新版工作流图](#附录新版工作流图)

---

## 一、项目通俗讲解

### 1.1 盼趣 AI 是什么

一个 **"AI 短剧工厂" SaaS**。用户在网页上做以下事情：

1. 填剧本
2. 自动生成角色形象
3. 生成场景图
4. 生成视频片段 / 配音
5. 加 BGM（**本仓库重点**）
6. 拼成成片

仓库里 99% 的文件是这套产品的**纯前端页面**（HTML + Tailwind/DaisyUI，无打包），主要给设计师 / 产品演示用。

### 1.2 BGM 模块在做什么

夹在仓库里的一个**独立 Python 实验**。流程一句话：

```
带时间戳的分镜剧本 (0-17s 紧张, 17-38s 悬疑...)
        ↓
GPT-5 分析每段情绪、强度
        ↓
GPT 输出一段英文音乐描述 (prompt + tags)
        ↓
扔给 Suno（在线 AI 作曲服务）生成
        ↓
pydub 把音乐剪到剧本总时长
        ↓
返回 mp3 给前端播放
```

### 1.3 打比方

像「点菜」：你告诉服务员（GPT）"我要酸甜口、5 分钟上桌"，服务员翻成厨师术语（"番茄、糖、醋、急火"），交给厨师（Suno）做出来。
**GPT 是翻译，Suno 是厨师**，BGM 模块就是中间的下单 + 收菜流水线。

---

## 二、现状梳理（代码层面）

### 2.1 涉及文件

| 文件 | 角色 |
|---|---|
| `test_bgm_timeline.py` | Flask 后端（端口 5002），3 个 endpoint |
| `Project/bgm-timeline.html` | 前端测试页，3 步流程 |
| `Project/test-audio-simple.html` | 输出文件播放/校验 |
| `CLAUDE.md` | 模块文档（**注意：内容与实际代码已脱节**） |

### 2.2 后端 endpoint

| 路径 | 作用 |
|---|---|
| `POST /api/script-to-prompt` | 剧本 → 提示词（两种模式：GPT-5 时间线 / 关键词匹配） |
| `POST /api/generate-direct` | 提示词 → 调 Suno → 下载 → 裁剪 → 返回 |
| `GET  /api/audio/<filename>` | 返回生成的 mp3 |

### 2.3 关键数据流

- **GPT 模板**：要求返回 JSON，包含 `timeline[]`（每段 `time_range / emotional_tone / intensity / music_suggestion`） + 一个总 `music_prompt`。
- **Suno 调用**：`POST https://api.bltcy.ai/suno/generate`，参数包括 `prompt / tags / title / mv: chirp-v4 / make_instrumental: true`。
- **音频后处理**：`pydub.AudioSegment.from_mp3 → audio[:target_ms] → export`。

### 2.4 内置基调表（关键词匹配模式）

7 种：紧张、悬疑、温馨、悲伤、恐惧、动作、励志。
每种有：中文关键词集 + 英文 `music_tags` + 一句英文 `description`。

### 2.5 硬性原则（CLAUDE.md 三次强调）

> ⚠️ **不要人声，必须纯音乐**。
> 提示词强制注入 `no vocals / no singing / no lyrics / instrumental only`，且 `make_instrumental: true`。

---

## 三、核心问题诊断

### 🔴 P0 问题 1：时间线分析了，但**没真用**

代码让 GPT 输出了完整的 `timeline[]`（4 段不同情绪），最后却**只取一个平均化的 prompt** 调一次 Suno，再粗暴切到时长。

**后果**：剧本里 4 段情绪起伏，最后听到的是一首平铺直叙的"差不多"音乐，戏剧张力全无。
**比喻**：点了"酸甜苦辣咸全要"，最后端上来一盘水煮白菜。

### 🔴 P0 问题 2：tags 里的"负面词"反而招来人声

```python
tags = "intense, suspense, ..., no vocals, no singing, no lyrics, instrumental only"
```

- Suno 的 `tags` 字段是**正向风格标签**，写否定式会被模型当成"提到人声"的提示，**反而更容易生成人声**。
- tags 通常有长度限制（≈120-200 字符），现在的拼接很容易超长被截断。
- 这与 CLAUDE.md 里"严禁人声"的最高原则**自相矛盾**。

### 🔴 P0 问题 3：prompt 没有"音乐工程师能用的硬指标"

只有形容词堆叠，**没指定 BPM、调式、乐器、制作风格、动态曲线**——这些才是 Suno 真正吃的硬参数。

> 例：`"intense, suspense, dramatic"` ≠ `"110bpm, D minor, ostinato strings, sub bass drone, sparse Zimmer-style"`

### 🟡 P1 问题 4：Suno 双候选只取一条

Suno 一次请求通常返回 2 个 clip，代码：

```python
clip_id = result['clips'][0]['id']
```

直接丢掉了另一个候选。**两个里挑好的**是免费的质量护栏，被浪费了。

### 🟡 P1 问题 5：暴力切音频，没有淡出

```python
trimmed_audio = audio[:target_ms]
```

结尾会"啪"一下断掉，听感非常业余。

### 🟡 P1 问题 6：响度没有归一

不同 prompt 生成的 BGM 音量参差，混入视频/语音轨时刺耳或被盖过。

### 🟢 P2 问题 7：无重试、无缓存、无评分

- Suno 失败（限流 / 内容审核 / 网络）就直接报错。
- 同样的 prompt 重复点会重新付费生成。
- 生成质量没有任何自动评估，全靠人耳。

### 🟢 P2 问题 8：工程隐患

- **API key 硬编码**在 `test_bgm_timeline.py:16` 和 `:265`，CLAUDE.md:181 也明文列出。仓库公开即泄露事故。
- `mv: 'chirp-v4'` 写死，Suno 模型迭代后无法切换。
- `check_links.js` 用了别人电脑的绝对路径 `/Users/chuckmi/...`，对其他开发机直接报错。
- CLAUDE.md 的目录结构、端口（5000）、文件名都与实际代码（端口 5002）对不上。

---

## 四、优化方案（按性价比排序）

### 🔥 P0-A：让时间线真正驱动生成

**三档可选方案**：

| 方案 | 做法 | 成本 | 张力 | 风格连贯 |
|---|---|---|---|---|
| **A. 分段独立生成 + crossfade** | 每段时间线单独调 Suno，pydub 做 2-3s 交叉淡入拼接 | ×N | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **B. 主题曲 + Stinger 叠加**（**推荐起步**） | 主轨用主导情绪生成一首贯穿整集；情绪突变点叠 5-10s 短音效（鼓击、提琴 stab、低频轰鸣） | ×1.5 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **C. Suno Continue/Extend** | 第一段正常生成，后续段用 `continue_clip_id` 在前一段尾部续写新情绪 | ×N | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**建议**：从 **B 起步**，改动最小、立刻能听出差异；预算充足后升 A 或 C。

### 🔥 P0-B：按 Suno 的脾气重写 prompt/tags

**改造规则**：

```diff
- tags = "intense, suspense, ..., no vocals, no singing, no lyrics, instrumental only"
+ tags = "cinematic orchestral, dark suspense, 110bpm, D minor, ostinato strings, sub bass, sparse"

- prompt = "[INSTRUMENTAL ONLY] High-stakes confrontation"
+ prompt = "[Instrumental, score only]\nA tense cinematic cue starting with sparse felt piano, sub bass drone enters at 0:08, ostinato strings build through 0:20, climax at 0:35 with low brass hits, fades to bass pulse at 0:55."
```

**核心要点**：

1. ✅ `tags` 只放**正向描述**：体裁、情绪、BPM、调式、乐器、制作风格参考。
2. ✅ `prompt` 顶部用 `[Instrumental]` / `[No vocals, score only]` **方括号标记式**指令（Suno 对此类标记响应最好）。
3. ✅ 保留 `make_instrumental: true`。
4. ✅ tags 长度控制在 **120 字符内**，高信号优先。
5. ❌ **不要在 tags 里写**任何形如 "no X" 的否定词。
6. ❌ **避开会暗示人声的体裁词**：pop, hip-hop, rock, ballad, anthem, choir 等。

### 🔥 P0-C：让 GPT 输出"音乐工程师能用的"结构化参数

把 GPT 模板从"返回一句 prompt"升级为"返回结构化音乐参数 JSON"：

```yaml
emotional_segment:
  bpm: 92                              # 在情绪表 BPM 范围内的精确值
  key: "D minor"                       # 调式决定底色
  instrumentation:                     # 3-5 件主要乐器，越具体越好
    - "felt piano (close mic)"
    - "muted cello"
    - "sub bass drone"
  production_style: "Hans Zimmer, Bladerunner 2049, sparse"
  dynamics_arc: "ppp → mp, single crescendo at 0:12"
  reference_tracks: ["Time - Hans Zimmer", "Bloom - Radiohead"]
  forbidden: ["drums", "vocals", "EDM"]
```

后端把这份 JSON **再 render 成 Suno 实际吃的 prompt 字符串**。等于给 Suno 配了个"作曲指挥"，而不是丢一堆形容词。

### 🟡 P1-A：双候选 + 自动质量护栏

```python
# 现在：
clip_id = result['clips'][0]['id']

# 改造：
candidates = [download(c) for c in result['clips']]  # 通常 2 个
scored = [(audio_quality_score(a, prompt_spec), a) for a in candidates]
best = max(scored, key=lambda x: x[0])[1]
```

**质量打分维度**：

- **人声能量检测**（Spleeter / librosa 频谱分析）：人声轨能量 > 阈值 → 直接拒收。
- **BPM 匹配**（`librosa.beat.beat_track`）：与请求 BPM 偏差 > 15% → 减分。
- **响度** 和 **频谱中心**：偏离基调期望范围 → 减分。
- 可选：再让 GPT-5 听摘要描述 + 文本对比要求做主观评分。

**这是唯一能根治"Suno 偷偷加人声"问题的护栏。**

### 🟡 P1-B：剪辑细节

```python
# 暴力切：
trimmed = audio[:target_ms]

# 改造：
trimmed = audio[:target_ms].fade_out(3000)        # 3 秒淡出
trimmed = loudness_normalize(trimmed, target_lufs=-18)  # 影视混音常用 LUFS
```

依赖：`pyloudnorm`（响度归一）、`pydub`（淡出已支持）。

### 🟢 P2-A：工程化护栏

| 项 | 现状 | 改造 |
|---|---|---|
| API key | 硬编码 | env var + `.env.example`；**立刻在两边平台 revoke 现有 key 重发** |
| Suno 重试 | 单次 | 3 次指数退避（1s, 4s, 16s） |
| 缓存 | 无 | prompt 的 SHA-256 哈希命中 → 复用 mp3 |
| 模型版本 | `chirp-v4` 写死 | 配置文件 / env，方便 A/B v4 / v4.5 / v5 |
| 日志 | print | 结构化 JSON 落盘（请求、Suno 返回的真实 tags、采纳与否） |
| 路径 | `output/` 硬编码 + 无 mkdir | `pathlib` + `mkdir(parents=True, exist_ok=True)` |

### 🟢 P2-B：基调音乐学参数表"喂死"

GPT 经常乱猜 BPM、调式。**直接在后端查表，GPT 只负责选基调和强度**。详见 [第五节](#五音乐学参数查表必背)。

### 🔵 P3：进阶玩法

- **风格一致性 / Leitmotif**：同一短剧每集复用 `style_reference` 或固定 seed/clip → 同一部戏的配乐听起来是一家人。
- **Spleeter 后处理**：万一 Suno 偷加了人声，用 Spleeter 把人声轨抠掉再合并。
- **自动评审闭环**：接入仓库里的 `auto-review-loop` skill，让 GPT 评分 → 不过关回炉，跑 2-3 轮自动收敛。
- **多模型 ensemble**：同一 prompt 同时丢给 Suno v4.5 和 v5（或其他作曲服务），算法挑分高的。

---

## 五、音乐学参数查表（必背）

供 GPT 模板和后端 render 共用。**GPT 选基调和强度，参数从表里取**，确定性立刻拉满。

| 基调 | BPM 区间 | 调式 | 核心乐器 | 制作风格参考 | 禁用 |
|---|---|---|---|---|---|
| **紧张** | 120-140 | D/A/E minor | ostinato 弦乐、sub bass、metallic perc | Hans Zimmer / Junkie XL | 大调 / 民谣木吉他 |
| **悬疑** | 70-90 | atonal / 调式模糊 | 不和谐 pad、prepared piano、low drone | Trent Reznor / Mica Levi | 鼓组 / 旋律性主题 |
| **温馨** | 75-95 | C/G major、Lydian、Mixolydian | felt piano、暖弦乐、木质打击 | Ludovico Einaudi / Joe Hisaishi | distortion / 808 bass |
| **悲伤** | 60-75 | A/E minor | 独奏大提琴或钢琴、长 reverb | Max Richter / Jóhann Jóhannsson | 鼓组 / 快速节奏 |
| **恐惧** | 50-70 | 不和谐音簇 | drone、不规则打击、风声、反向钢琴 | Mica Levi (Under the Skin) | 旋律主题 / 大调 |
| **动作** | 140-170 | D/F minor | 混合管弦 + 电子鼓、铜管 stab、taiko | Lorne Balfe / Brian Tyler | 慢节奏 / 钢琴独奏 |
| **励志** | 100-120 | C/D/F major（多用上行） | 渐进弦乐、号声、合唱式 swell | Steve Jablonsky / Two Steps From Hell | 小调 / 极简 |

**Render 模板示例**（紧张 / 强度 7）：

```
tags: cinematic orchestral, dark suspense, 128bpm, D minor, ostinato strings, sub bass, hybrid percussion, Zimmer-style
prompt:
[Instrumental, score only]
A high-tension cinematic cue at 128bpm in D minor.
Open with sparse sub bass drone and muted ostinato strings.
Add metallic percussion stabs from 0:08.
Build with low brass crescendo at 0:20.
Climax at 0:35 with full string ensemble and taiko hits.
Resolve to bass pulse and reverb tail by 0:55.
```

---

## 六、推荐落地路线图

### Sprint 1（半天，性价比最高）

**目标**：听感立刻上一个档次，安全隐患归零。

- [ ] 移除 tags 里所有 "no X" 否定词，改成正向标签
- [ ] prompt 顶部加 `[Instrumental, score only]` 方括号指令
- [ ] 结尾 `fade_out(3000)` + 响度归一到 -18 LUFS
- [ ] API key 移到 env var；旧 key 在平台 revoke
- [ ] `chirp-v4` 字符串改成 env / config 项

### Sprint 2（1-2 天，效果质变）

**目标**：单集情绪有起伏，工程可观测。

- [ ] 实现 [第五节](#五音乐学参数查表必背)查表，写入 `tone_params.py`
- [ ] 升级 GPT 模板为"结构化音乐参数 JSON"
- [ ] 后端写 `render_suno_payload(tone, params)` 把 JSON → Suno prompt
- [ ] Suno 双候选都下载，加**人声能量检测**做最低门槛过滤
- [ ] Suno 调用加 3 次指数退避重试
- [ ] 请求/响应 JSON 落盘日志

### Sprint 3（2-3 天，进入产品级）

**目标**：时间线真正可用 + 多集风格统一。

- [ ] 实现"主题曲 + Stinger" 拼接（方案 B）
- [ ] prompt 哈希缓存层
- [ ] 同一短剧 ID 维度复用 style/seed → 多集 leitmotif
- [ ] 接入 `auto-review-loop` 自动评分回炉机制

### Sprint 4（可选，研究向）

- [ ] 调研 Suno Continue/Extend，实现方案 C
- [ ] Spleeter 兜底去人声
- [ ] 多模型 ensemble

---

## 附录：新版工作流图

```text
                 剧本 (含 0-17s / 17-38s 时间线)
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  GPT-5（受查表约束）             │
        │  输出结构化 JSON：               │
        │   - 主导基调                     │
        │   - 每段 emotion/intensity       │
        │   - dynamics_arc                 │
        └──────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  后端 render_suno_payload()      │
        │   - 查 tone_params 表            │
        │   - 拼正向 tags（≤120 字符）     │
        │   - prompt 含 [Instrumental] 前缀 │
        │   - 主轨 1 个 + Stinger N 个     │
        └──────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  Suno API（3 次重试、双候选）    │
        │  返回 2 clip                     │
        └──────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  质量护栏                        │
        │   - 人声能量检测（拒收阈值）     │
        │   - BPM 匹配度打分               │
        │   - 必要时回炉                   │
        └──────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │  拼接 / 剪辑                     │
        │   - 主轨 + Stinger crossfade     │
        │   - fade_out 3s                  │
        │   - LUFS 归一 (-18)              │
        └──────────────────────────────────┘
                          │
                          ▼
              落盘 + 哈希缓存 + 日志
                          │
                          ▼
                       前端播放
```

---

## 一句话总结

> 当前 BGM 模块**最大的浪费**是：花了 GPT 钱分析出完整时间线，却只给 Suno 下一道"平均口味"的菜单。
> 改造的核心思路是：**让 GPT 输出音乐工程师能用的硬参数，让 Suno 按时间线吃多份订单，最后用工程手段拼出有情绪起伏、有质量护栏、有风格连贯性的成片配乐**。

收益预期（按 Sprint 1+2 落地后体感）：

- 人声泄露率：30%+ → < 3%
- 情绪贴合度：用户主观打分提升 1 档以上
- 单集 BGM 平均重生成次数：3-5 次 → 1-2 次
- API 成本：缓存命中后下降 20-40%
