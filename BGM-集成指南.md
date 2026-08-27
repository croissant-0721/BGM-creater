# BGM 生成工具 · 集成指南

> 面向"把这套自动配乐能力集成进另一个项目"的工程文档。
> 对应代码：分支 `feat/bgm-v2-suno-aware-pipeline`，包目录 `bgm_v2/`。

---

## 1. 这是什么

输入**带时间/情绪信息的剧本（或分镜表）**，自动产出**与剧情情绪同步的纯器乐 BGM**（mp3）。

核心能力：
- 把剧本按情绪切成多段，**每种情绪单独用 Suno 生成**，再按过渡类型 crossfade 拼成一条连续曲；
- 在剧情高潮/反转的精确时间点叠加 **stinger 卡点重音**（合成的低频砸下 / 前导渐强 / 悬疑下坠）；
- 成品**时长精确等于剧本总时长**（绝不超、不错位）；
- 段间响度统一（-18 LUFS）、结尾淡出；
- Suno 双候选打分挑优、失败重试、按 prompt 哈希缓存（同输入复用、不重复付费）；
- 多段**并发生成**，整集耗时≈最慢一段。

> 纯音乐、无人声是硬性目标（`make_instrumental` + prompt 约束）。

---

## 2. 一图流（数据流）

```
剧本/分镜文本 ──(可选)── GPT 解析 ──► analysis(情绪时间线 JSON)
                                          │
                         detect_emotional_cues：切分/平铺/算过渡
                                          ▼
                    每种情绪调一次 Suno(并发) ──► 原始候选(双)──► 打分挑优
                                          ▼
                每个 cue 从所属情绪候选按"自己的精确时长"裁剪
                                          ▼
              按过渡类型 crossfade 拼接 + 卡点 stinger 叠加
                                          ▼
              硬卡到总时长 + 淡出 + LUFS 归一 ──► episode_final.mp3
```

---

## 3. 模块职责

```
bgm_v2/
├── config.py                 # env 驱动的配置(Config)：key/base/model/目录/LUFS/重试
├── gpt_analyzer.py           # 自由剧本文本 → 结构化 analysis(timeline)；normalize_tone
├── storyboard.py             # 分镜表文本 → analysis(shots[] + cues[])（GPT）
├── tone_params.py            # 12 种情绪的音乐学查表(BPM/调式/乐器/风格) + payload 渲染
├── suno_client.py            # 云雾 Suno：提交 + 轮询 + 重试 + 缓存 + 双候选下载
├── quality.py                # 候选打分(BPM 匹配等)；⚠️ vocal_energy_ratio 不可信(见 §10)
├── post.py                   # 裁剪/淡出/LUFS 归一/crossfade 拼接
├── stinger.py                # 卡点重音合成(impact/riser/sub_drop) + 镜头级分情绪挑点
├── multisegment_pipeline.py  # 【主推荐】多段生成+拼接+卡点+并行
└── pipeline.py               # 单轨/分镜单曲 pipeline(见 §4)
```

---

## 4. 三条可用 pipeline（选哪条）

| 入口函数 | 产物 | 情绪处理 | 适用 |
|---|---|---|---|
| **`generate_bgm_multisegment`** ✅推荐 | `episode_final.mp3` | **每情绪单独生成+拼接+多卡点** | 情绪有起伏的剧集，要"卡点" |
| `generate_bgm_v2` | `{情绪}_{时长}s_v2_{时间戳}.mp3` | 取主导情绪一首到底 + 1 个 stinger | 想要连贯单曲、便宜、无接缝 |
| `generate_bgm_from_storyboard` | 单曲 | 单曲但 prompt 走完整情绪弧线，无 stinger | 分镜驱动的单曲 |

下文以**多段 pipeline**为主。

---

## 5. 快速集成（最小可用）

### 5.1 依赖

```bash
pip install requests pydub librosa numpy pyloudnorm soundfile python-dotenv
pip install python-docx          # 仅当需要直接读 .docx 分镜
# 系统需有 ffmpeg（务必在 PATH 中）：
#   macOS:  brew install ffmpeg
#   ubuntu: apt-get install ffmpeg
```
> Python ≥ 3.9。`flask/flask-cors` 只有跑旧的独立 HTTP 服务才需要，库式集成不需要。

### 5.2 配置（env）

复制 `bgm_v2/.env.example` 为 `.env` 并填 key。**默认已走云雾(yunwu)，GPT 与 Suno 用同一把云雾 key 即可**：

```bash
BGM_GPT_API_KEY=sk-你的云雾key
BGM_GPT_API_BASE=https://yunwu.ai/v1
BGM_GPT_MODEL=gpt-5.4
BGM_SUNO_API_KEY=sk-你的云雾key
BGM_SUNO_API_BASE=https://yunwu.ai/suno
BGM_SUNO_MODEL=chirp-v4            # 可换 chirp-v4-5 / chirp-v5
BGM_OUTPUT_DIR=/你的项目/bgm_out
BGM_CACHE_DIR=/你的项目/bgm_cache
```
也可在代码里 `os.environ[...]=...`（须在 `import bgm_v2` 之前设置），或直接改 `Config` 实例字段。

### 5.3 调用 A：自己已有情绪时间线（**不调 GPT**，最省事/可控）

如果宿主项目已经知道每段的情绪和时长，直接构造 `analysis`，跳过 GPT：

```python
import os
os.environ.setdefault("BGM_SUNO_API_KEY", "sk-...")
os.environ.setdefault("BGM_SUNO_API_BASE", "https://yunwu.ai/suno")

from pathlib import Path
from bgm_v2.config import Config
from bgm_v2.multisegment_pipeline import generate_bgm_multisegment

analysis = {
    "title": "EP1",
    "primary_tone": "紧张",
    "primary_intensity": 8,
    "total_duration": 60,            # 秒；也可用 "total_duration_s"
    "timeline": [
        {"duration": 20, "emotional_tone": "紧张", "intensity": 8, "scene_description": "雨夜对峙"},
        {"duration": 25, "emotional_tone": "温馨", "intensity": 5, "scene_description": "和解"},
        {"duration": 15, "emotional_tone": "悬疑", "intensity": 7, "scene_description": "反转钩子"},
    ],
}

cfg = Config()
result = generate_bgm_multisegment(analysis, "EP1", Path(cfg.output_dir) / "ep1", config=cfg)
print(result["final_audio"])        # 成品 mp3 路径
```

### 5.4 调用 B：从分镜表/剧本文本起（**走 GPT 解析**）

```python
from bgm_v2.config import Config
from bgm_v2.storyboard import analyze_storyboard          # 分镜表 → cues
from bgm_v2.multisegment_pipeline import generate_bgm_multisegment

cfg = Config()
# 分镜文本：每行 "第N场 | 时长s | 画面描述(可含台词/信息点)"
analysis = analyze_storyboard(storyboard_text, "EP1", cfg)
result = generate_bgm_multisegment(analysis, "EP1", Path(cfg.output_dir) / "ep1", config=cfg)
```
> 自由剧本文本(无分镜)用 `from bgm_v2.gpt_analyzer import analyze_script_structured`，
> `analyze_script_structured(script_text, "EP1", cfg)` → 返回 timeline 形态的 analysis。

---

## 6. 输入格式（`analysis`）

`generate_bgm_multisegment` / `detect_emotional_cues` 接受**两种形态**，二选一即可：

**形态 A — timeline（适合自己拼）**
```jsonc
{
  "title": "EP1",
  "primary_tone": "紧张",          // 主基调（缺省会推断）
  "primary_intensity": 8,
  "total_duration": 60,            // 或 "total_duration_s"
  "timeline": [
    {"duration": 20, "emotional_tone": "紧张", "intensity": 8, "scene_description": "..."},
    ...
  ]
}
```

**形态 B — cues（`analyze_storyboard` 的输出）**
```jsonc
{
  "title": "EP1", "total_duration_s": 64, "primary_tone": "紧张", "primary_intensity": 9,
  "shots": [ {"start_s":0,"end_s":3,"tone":"紧张","intensity":8,"narrative_func":["冲突"], ...} ],
  "cues":  [ {"start_s":0,"end_s":31,"tone":"紧张","intensity_peak":9,"narrative_summary":"...",
              "transition_in":"cold","transition_out":"swell"}, ... ]
}
```

**12 种合法情绪(tone)**：`紧张 / 悬疑 / 温馨 / 悲伤 / 恐惧 / 动作 / 励志 / 羞辱 / 静默 / 反击 / 豪门 / 异常`。
其他写法会被 `normalize_tone` 归一到这 12 种。stinger 卡点也依赖 `shots[].narrative_func` 与强度（见 §9）。

---

## 7. 输出

**返回值**（`generate_bgm_multisegment` → dict）：
```jsonc
{
  "pipeline": "multisegment",
  "total_duration_s": 64,
  "final_audio": ".../episode_final.mp3",     // ← 成品
  "segments": [ {"cue_id":1,"start_s":0,"end_s":31,"duration_s":31,"tone":"紧张",
                 "transition":"cold","audio":".../segments/cue_1_紧张.mp3"}, ... ],
  "cues": [...],                               // 最终分段（含 transition_from_previous）
  "unique_segments": 4,                        // 实际调用 Suno 的次数
  "unique_tones": ["紧张","静默","温馨","悬疑"],
  "stingers": [ {"ts_ms":7000,"kind":"impact","gain_db":-9}, ... ]
}
```

**落盘文件**（在 `out_dir`）：
- `episode_final.mp3` — 最终成品（**集成方取这个**）
- `segments/cue_N_<情绪>.mp3` — 各分段中间产物（调试用）
- 缓存在 `cfg.cache_dir`：`<hash>__cand{0,1}__<clipId>.mp3` + `<hash>__payload.json`

---

## 8. 关键参数

`generate_bgm_multisegment(analysis, title, out_dir, *, config=None, use_stinger=True, parallel=True, submit_stagger_s=3.0)`

| 参数 | 默认 | 说明 |
|---|---|---|
| `use_stinger` | True | 是否叠加卡点重音 |
| `parallel` | True | 并发生成所有情绪（错开 `submit_stagger_s` 秒提交防限流）；False 则串行(每段间等 30s) |
| `submit_stagger_s` | 3.0 | 并发时提交错峰秒数 |
| `config` | None | 传 `Config()`；不传则用 env 新建 |

`Config` 常用字段：`target_lufs=-18.0`、`fade_out_ms=3000`、`suno_poll_timeout_s=900`、`suno_max_retries=5`、`suno_model`、`output_dir`、`cache_dir`。

---

## 9. 情绪/卡点机制（决定听感）

- **分段**：`tone` 变化、强度跳变 ≥3、或叙事节点（反转/真相/胜利/泼酒…）处强制切；每段 6–30s；相邻同情绪且强度相近会合并。
- **同情绪复用**：同一情绪只调一次 Suno，其余 cue 复用该候选但**按各自时长重裁**（省钱且不超时）。
- **过渡**：`continue 1200ms / gradual 1000ms / abrupt 800ms / dramatic 700ms` crossfade（无 0ms 硬切，听感顺）。
- **卡点 stinger**（镜头级、分情绪）：
  - 紧张/反击/羞辱… 的反转/结果/关键动作节拍 → `impact`（低频砸下，强度≥8 加前导 riser）
  - 悬疑/异常/恐惧 的钩子 → `sub_drop`（阴森低频下坠）
  - **温馨/励志（求婚等柔情）→ 不砸**
- ⚠️ **卡点精度 = 输入时间线精度**：现在的时间来自 GPT 读分镜的估时。要真正卡到**剪好的成片**，需喂入成片的真实切点时间戳（如对视频做镜头切分检测）。

---

## 10. 已知坑 / 注意事项

1. **ffmpeg 必须在系统 PATH**。`__init__.py`/`post.py` 里有一段写死的 Windows ffmpeg 路径，但有 `os.path.exists` 守卫，非 Windows 会跳过并回落到 PATH 里的 ffmpeg。
2. **`vocal_energy_ratio` 不可信**：它对温馨/静默这类中频满的器乐会**误报人声**（实听无人声）。**不要据它做"人声拒收"门控**。它仍占候选打分 0.7 权重，若要改评分可降此权重、改靠 BPM/响度。
3. **BPM 常对不准**：Suno 灵感模式不太吃精确 BPM，属已知现象，不影响情绪贴合。
4. **缓存**：按 payload 的 SHA-256 命中复用 mp3 → 同输入重跑免费、秒回；`cache_dir` 会增长，按需清理。
5. **GPT 可选**：宿主项目若已有情绪时间线，直接构造 `analysis`（形态 A）跳过 GPT，省一次调用、也更可控。
6. **耗时/成本**：每个唯一情绪 ≈ 一次 Suno 调用(~0.2–0.3 元、~60–120s)；并行下整集 ≈ 最慢一段。GPT 解析约 1 次调用。
7. **商务**：云雾**能否开发票**尚未与其客服确认；若需报销请先确认。
8. 当前代码在 `feat/bgm-v2-suno-aware-pipeline` 分支，尚未并入 master。

---

## 11. 三种集成方式

**A. 作为 Python 库（推荐，宿主是 Python）**
把整个 `bgm_v2/` 目录拷进宿主项目（或装成内部包），`from bgm_v2.multisegment_pipeline import generate_bgm_multisegment` 直接调。配好 env/Config 即可。

**B. 子进程 / CLI**
写一个 thin runner（设 env → 调函数 → 把返回 dict 打成 JSON 落盘/打印），宿主用 `subprocess` 调用、读 `final_audio` 路径与 JSON。适合宿主非 Python。

**C. HTTP 微服务（推荐，跨语言/解耦）**
用 FastAPI/Flask 包一个 `POST /bgm`：收 `analysis`(或剧本文本) → 调 `generate_bgm_multisegment` → 返回 `final_audio` 文件或可下载 URL。生成耗时较长，建议**异步任务 + 轮询/回调**（提交返回 task_id，轮询查状态——和 Suno 自身的异步模式一致）。仓库根的旧 `test_bgm_timeline.py` 是个 Flask 参考实现（端点/字段已过时，仅作结构参考）。

---

## 12. 接口速查

```python
# 配置
from bgm_v2.config import Config;  cfg = Config()

# 解析（二选一，或自己构造 analysis）
from bgm_v2.storyboard import analyze_storyboard           # 分镜表 → cues
from bgm_v2.gpt_analyzer import analyze_script_structured  # 自由剧本 → timeline

# 生成（主推荐）
from bgm_v2.multisegment_pipeline import generate_bgm_multisegment, detect_emotional_cues
result = generate_bgm_multisegment(analysis, "EP1", out_dir, config=cfg,
                                   use_stinger=True, parallel=True)

# 备选 pipeline
from bgm_v2.pipeline import generate_bgm_v2, generate_bgm_from_storyboard
```

---

## 13. 一句话给集成方

> 配好云雾 key（GPT/Suno 同一把）→ 构造 `analysis`（自己拼时间线最省事）→ 调 `generate_bgm_multisegment` → 取返回里的 `final_audio`。其余（分段、卡点、拼接、时长、响度、重试、缓存）pipeline 内部已处理。
