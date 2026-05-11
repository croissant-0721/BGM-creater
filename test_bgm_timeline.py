#!/usr/bin/env python3
# 智能时间线BGM测试服务器 - 支持分镜时间解析和情感渐变
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import requests
from datetime import datetime
import json
import re
import time

app = Flask(__name__, static_folder='Project')
CORS(app)

# GPT-5.4 API配置
GPT_API_KEY = "sk-3V42XPHA7lJrC9yVDReoOWvAvaFaPgzv4pjebdLac7MxmzEj"
GPT_API_BASE = "https://yunwu.ai/v1"

# 情感基调关键词映射
TONE_KEYWORDS = {
    '紧张': {
        'keywords': ['紧张', '危险', '追杀', '对峙', '逃跑', '追逐', '生死', '威胁', '压力', '紧迫'],
        'music_tags': 'intense, suspense, dramatic, dark, aggressive, pounding, pressure',
        'description': 'High-stakes confrontation, life or death situation'
    },
    '悬疑': {
        'keywords': ['悬疑', '神秘', '谜团', '疑点', '真相', '线索', '秘密', '发现', '揭露', '隐藏'],
        'music_tags': 'mysterious, ambient, minimal, electronic, synthesizer, dark, atmospheric',
        'description': 'Mystery and suspense'
    },
    '温馨': {
        'keywords': ['温馨', '治愈', '温暖', '浪漫', '甜蜜', '重逢', '家庭', '友谊', '爱情', '陪伴'],
        'music_tags': 'warm, gentle, strings, melodic, atmospheric, cinematic',
        'description': 'Warm emotional atmosphere'
    },
    '悲伤': {
        'keywords': ['悲伤', '痛苦', '失去', '死亡', '分离', '牺牲', '绝望', '遗憾', '哀悼', '哭泣'],
        'music_tags': 'melancholic, emotional, cello, slow, orchestral, atmospheric',
        'description': 'Sad and emotional moment'
    },
    '恐惧': {
        'keywords': ['恐惧', '恐怖', '惊吓', '噩梦', '幽灵', '黑暗', '惊悚', '害怕', '颤抖', '尖叫'],
        'music_tags': 'dark, ominous, threatening, deep, heavy, bass, danger, brooding',
        'description': 'Fear and horror atmosphere'
    },
    '动作': {
        'keywords': ['动作', '打斗', '战斗', '枪战', '武打', '格斗', '追击', '反击'],
        'music_tags': 'intense, fast, aggressive, driving, relentless, action, chase',
        'description': 'Fast-paced action'
    },
    '励志': {
        'keywords': ['励志', '成长', '希望', '梦想', '奋斗', '坚持', '突破', '胜利', '信念', '勇气'],
        'music_tags': 'uplifting, epic, cinematic, inspiring, orchestral',
        'description': 'Uplifting and inspiring'
    }
}


def trim_audio_to_duration(audio_path, target_duration, tone):
    """裁剪音频到目标时长

    Args:
        audio_path: 原始音频文件路径
        target_duration: 目标时长（秒）
        tone: 情感基调

    Returns:
        裁剪后的音频文件路径
    """
    try:
        from pydub import AudioSegment

        # 加载音频
        audio = AudioSegment.from_mp3(str(audio_path))
        original_duration = len(audio) / 1000  # 转换为秒

        print(f"[INFO] Original audio duration: {original_duration:.2f}s")
        print(f"[INFO] Target duration: {target_duration}s")

        # 如果目标时长大于等于原始时长，不裁剪
        if target_duration >= original_duration:
            print(f"[INFO] Target duration >= original duration, no trimming needed")
            return audio_path

        # 裁剪音频（从开始到目标时长）
        target_ms = int(target_duration * 1000)
        trimmed_audio = audio[:target_ms]

        # 保存裁剪后的音频
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{tone}_{target_duration}s_{timestamp}.mp3'
        output_path = Path('output') / filename

        trimmed_audio.export(str(output_path), format='mp3')

        print(f"[SUCCESS] Audio trimmed from {original_duration:.2f}s to {target_duration}s")
        print(f"[SUCCESS] Saved: {output_path}")

        return output_path

    except ImportError:
        print("[WARNING] pydub not installed, skipping audio trimming")
        print("[INFO] Install pydub: pip install pydub")
        print("[INFO] Also install ffmpeg: https://ffmpeg.org/download.html")
        return audio_path
    except Exception as e:
        print(f"[ERROR] Audio trimming failed: {e}")
        print(f"[INFO] Using original audio file")
        return audio_path


def analyze_script_with_timeline(script_text, script_title):
    """使用GPT-5.4分析剧本并生成带时间线的BGM提示词"""

    prompt = f"""你是一位专业的电影音乐制作人。请根据以下分镜剧本，生成带时间线的BGM（背景音乐）提示词。

剧本标题：{script_title}

剧本内容：
{script_text[:5000]}

请返回JSON格式：
{{
    "total_duration": "总时长（秒）",
    "timeline": [
        {{
            "time_range": "0-17s",
            "duration": 17,
            "scene_description": "场景描述",
            "emotional_tone": "紧张/悬疑/温馨/悲伤/恐惧/动作/励志",
            "intensity": 1-10,
            "music_suggestion": "这个段落的音乐建议"
        }}
    ],
    "emotional_arc": "情感曲线描述",
    "primary_tone": "主导情感基调",
    "confidence": 0.9,
    "tone_explanation": "为什么选择这个基调",
    "music_prompt": {{
        "prompt": "完整的音乐生成提示词，必须包含时间线描述",
        "tags": "音乐标签，必须包含: no vocals, no singing, no lyrics, instrumental only",
        "title": "{script_title} - BGM"
    }},
    "analysis_summary": "简要分析总结"
}}

只返回JSON，不要其他内容。"""

    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": "你是一位专业的电影音乐制作人"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(
        f"{GPT_API_BASE}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    result = response.json()
    content = result['choices'][0]['message']['content']
    return json.loads(content)


def analyze_script_keywords(script_text, script_title):
    """使用关键词匹配分析剧本"""
    tone_scores = {}
    for tone, config in TONE_KEYWORDS.items():
        score = sum(1 for keyword in config['keywords'] if keyword in script_text)
        tone_scores[tone] = score

    primary_tone = max(tone_scores.items(), key=lambda x: x[1]) if tone_scores else ('中性', 0)
    confidence = min(primary_tone[1] / 5.0, 1.0)

    tone_config = TONE_KEYWORDS.get(primary_tone[0], TONE_KEYWORDS['紧张'])

    # 提取时间信息
    time_pattern = r'(\d+)-(\d+)s'
    time_matches = re.findall(time_pattern, script_text)
    total_duration = 80

    if time_matches:
        last_end = max(int(end) for start, end in time_matches)
        total_duration = last_end

    return {
        'primary_tone': primary_tone[0],
        'confidence': confidence,
        'total_duration': total_duration,
        'music_prompt': {
            'prompt': f"[INSTRUMENTAL ONLY] {tone_config['description']}",
            'tags': f"{tone_config['music_tags']}, no vocals, instrumental only",
            'title': f"{script_title} - {primary_tone[0]} BGM",
            'mv': 'chirp-v4',
            'make_instrumental': True
        }
    }


@app.route('/api/script-to-prompt', methods=['POST'])
def script_to_prompt():
    """剧本转提示词"""
    try:
        data = request.get_json()
        script_text = data.get('script_text', '')
        script_title = data.get('script_title', 'Untitled')
        use_gpt = data.get('use_gpt_analysis', False)

        if not script_text or len(script_text) < 10:
            return jsonify({'success': False, 'error': '剧本内容太短'}), 400

        if use_gpt:
            gpt_result = analyze_script_with_timeline(script_text, script_title)
            bgm_prompt = gpt_result['music_prompt']
            bgm_prompt['mv'] = 'chirp-v4'
            bgm_prompt['make_instrumental'] = True

            return jsonify({
                'success': True,
                'script_info': {
                    'title': script_title,
                    'primary_tone': gpt_result.get('primary_tone', ''),
                    'total_duration': gpt_result.get('total_duration', 0)
                },
                'analysis': gpt_result,
                'bgm_prompt': bgm_prompt
            })
        else:
            result = analyze_script_keywords(script_text, script_title)
            return jsonify({
                'success': True,
                'script_info': {
                    'title': script_title,
                    'primary_tone': result['primary_tone'],
                    'total_duration': result['total_duration']
                },
                'analysis': result,
                'bgm_prompt': result['music_prompt']
            })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-direct', methods=['POST'])
def generate_direct():
    """生成BGM"""
    try:
        data = request.get_json()
        prompt_data = data.get('prompt_data')

        api_key = "sk-reng5aEQBJBwT8KpmsSYopmunwbRBMw4zJA95XHJ1jgNNmCe"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        music_prompt = prompt_data['bgm_prompt']

        response = requests.post(
            "https://api.bltcy.ai/suno/generate",
            headers=headers,
            json=music_prompt,
            timeout=60
        )

        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'Suno API error: {response.status_code}'}), 500

        result = response.json()
        clip_id = result['clips'][0]['id']

        # 轮询等待完成
        start = time.time()
        while time.time() - start < 300:
            check_response = requests.get(
                f"https://api.bltcy.ai/suno/feed/{clip_id}",
                headers=headers,
                timeout=30
            )

            clip_data = check_response.json()

            for clip in clip_data:
                if clip.get('id') == clip_id:
                    status = clip.get('status')
                    if status == 'complete':
                        audio_url = clip.get('audio_url')
                        if audio_url:
                            # 下载音频
                            audio_response = requests.get(audio_url, stream=True, timeout=60)

                            temp_filepath = Path('output') / f'temp_{clip_id}.mp3'
                            with open(temp_filepath, 'wb') as f:
                                for chunk in audio_response.iter_content(chunk_size=8192):
                                    f.write(chunk)

                            # 裁剪音频
                            target_duration = prompt_data['script_info'].get('total_duration', 80)
                            final_filepath = trim_audio_to_duration(temp_filepath, target_duration, prompt_data['script_info']['primary_tone'])

                            # 删除临时文件
                            if final_filepath != temp_filepath and temp_filepath.exists():
                                temp_filepath.unlink()

                            return {
                                'success': True,
                                'audio_file': f'/api/audio/{final_filepath.name}',
                                'tone': prompt_data['script_info']['primary_tone']
                            }

                    elif status == 'failed':
                        return jsonify({'success': False, 'error': 'Generation failed'}), 500

            time.sleep(10)

        return jsonify({'success': False, 'error': 'Timeout'}), 500

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/audio/<filename>')
def get_audio(filename):
    """获取音频文件"""
    try:
        from urllib.parse import unquote
        filename = unquote(filename)
        filepath = Path('output') / filename
        if filepath.exists():
            return send_file(str(filepath), mimetype='audio/mpeg')
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("智能时间线BGM服务器 - 端口 5002")
    print("=" * 60)
    print(" * Running on http://127.0.0.1:5002")
    print()

    app.run(host='0.0.0.0', port=5002, debug=False)
