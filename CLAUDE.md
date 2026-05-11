# Panqu Project - Short Drama BGM Generator

## 项目概述

短剧项目，支持从剧本自动生成BGM（背景音乐）。核心需求是生成**100%纯音乐**，严禁任何人声。

## 核心技术栈

- **Python**: 后端服务
- **Flask**: Web API服务器
- **柏拉图AI Suno API**: 音乐生成
- **GPT-5.4 API**: 剧本分析和提示词生成
- **Tailwind CSS + DaisyUI**: 前端UI

## 目录结构

```
panqu-project/
├── drama-generator.py          # BGM生成器核心类
├── script_to_prompt_converter.py  # 剧本转提示词转换器
├── bgm_server.py               # Flask Web服务器
├── .skills/                    # Claude Code Skills
│   ├── bgm-prompt-generator.md
│   └── generate-bgm-prompt.md
├── Project/                    # 前端页面
│   ├── project-script-bgm-test.html  # 测试页面
│   └── project-script-bgm.html       # 完整功能页面
├── output/                     # 生成的BGM文件存放
└── ideas/                      # 创作规范
```

## 重要原则

### ⚠️ 严禁人声原则
用户明确要求：**"不要有歌词"**，所有生成的BGM必须：
- ✅ 纯音乐，无任何人声
- ✅ 添加标签：no vocals, no singing, no lyrics
- ✅ 使用参数：make_instrumental: true
- ❌ 绝不能生成带人声的歌曲

### 匹配剧情和时长
- 分析剧本情感基调（紧张/温馨/悬疑/悲伤等）
- 匹配场景情绪和节奏
- 考虑剧本/场景时长，生成合适长度的音乐

## Claude Code Skills

项目包含2个自定义skills，用于规范化BGM提示词生成：

### 1. `/generate-bgm-prompt`
从剧本内容生成BGM提示词。

**使用方式：**
```
请为以下剧本生成BGM提示词：
[粘贴剧本内容]
```

**功能：**
- 自动分析剧本情感基调
- 生成详细的英文音乐描述
- **强制添加无人声标签**
- 匹配剧情走向和时长
- 提供音乐设计说明

### 2. `bgm-prompt-generator`
底层skill，定义BGM生成的核心规则和质量检查。

## API接口

### Web服务器 (bgm_server.py)
- **启动**: `python bgm_server.py`
- **地址**: http://localhost:5000
- **健康检查**: GET /api/health

### 核心API端点

#### 1. 剧本转提示词
```
POST /api/script-to-prompt
Content-Type: application/json

{
  "script_text": "剧本内容...",
  "script_title": "剧本标题",
  "use_gpt_analysis": true  // 是否使用GPT-5.4分析
}

Response:
{
  "success": true,
  "script_info": {
    "title": "剧本标题",
    "primary_tone": "紧张",
    "confidence": 0.92
  },
  "analysis": {
    "primary_tone": "紧张",
    "tone_explanation": "...",
    "scene_count": 18,
    "used_gpt_analysis": true
  },
  "bgm_prompt": {
    "prompt": "[INSTRUMENTAL ONLY]\nTitle: ...",
    "tags": "intense, suspense, no vocals, instrumental only...",
    "title": "剧本标题 - 紧张 BGM",
    "mv": "chirp-v4",
    "make_instrumental": true
  }
}
```

#### 2. 提示词转BGM
```
POST /api/prompt-to-bgm
Content-Type: application/json

{
  "prompt_data": {
    "script_info": {...},
    "bgm_prompt": {...}
  }
}

Response:
{
  "success": true,
  "script_title": "剧本标题",
  "tone": "紧张",
  "audio_file": "/api/audio/紧张_from_script_20260502_123456.mp3",
  "generated_at": "20260502_123456"
}
```

## 前端页面

### 测试页面 (推荐)
```
http://localhost:5000/Project/project-script-bgm-test.html
```
简化版测试页面，3步流程：
1. 上传剧本（可选GPT-5.4分析）
2. 查看生成的提示词
3. 生成BGM

### 完整功能页面
```
http://localhost:5000/Project/project-script-bgm.html
```
4步向导式页面，包含更多配置选项。

## 开发工作流

### 添加新的BGM生成功能
1. 生成BGM提示词时，使用 `/generate-bgm-prompt` skill
2. 确保**所有**提示词包含无人声标签
3. 检查提示词是否匹配剧本情感和时长

### 修改BGM生成逻辑
- 主要逻辑在 `drama-generator.py` 的 `BGMGenerator` 类
- 提示词生成在 `script_to_prompt_converter.py`

### 测试API
```bash
# 测试剧本分析
curl -X POST http://localhost:5000/api/script-to-prompt \
  -H "Content-Type: application/json" \
  -d '{"script_text": "测试剧本", "use_gpt_analysis": true}'

# 测试BGM生成
python -c "
from drama_generator import BGMGenerator
gen = BGMGenerator('your-api-key')
# ... 生成BGM
"
```

## API密钥配置

- **柏拉图AI (Suno)**: `sk-reng5aEQBJBwT8KpmsSYopmunwbRBMw4zJA95XHJ1jgNNmCe`
- **GPT-5.4**: `sk-3V42XPHA7lJrC9yVDReoOWvAvaFaPgzv4pjebdLac7MxmzEj`

## 快速开始

### 1. 启动服务器
```bash
cd "d:\1 a universe\panqu-project"
python bgm_server.py
```

### 2. 访问测试页面
打开浏览器访问：
```
http://localhost:5000/Project/project-script-bgm-test.html
```

### 3. 生成BGM
1. 粘贴剧本内容
2. 勾选"使用GPT-5.4智能分析"
3. 点击"测试剧本分析"
4. 查看提示词
5. 点击"生成BGM"

## 注意事项

- ⚠️ **所有BGM必须无人声** - 这是用户的明确要求
- ⚠️ GPT-5.4分析需要等待API响应（可能需要10-30秒）
- ⚠️ BGM生成需要1-2分钟
- ✅ 生成的BGM文件保存在 `output/` 目录

## 相关文件

- [example_script.txt](example_script.txt) - 示例剧本
- [output/prompt_example_script_*.json](output/) - 提示词示例
- [.skills/](.skills/) - Claude Code技能定义
