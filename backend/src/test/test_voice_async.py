#!/usr/bin/env python3
import sys
import os
import asyncio

# 将 backend/src 加入导入路径
script_dir = os.path.dirname(__file__)
backend_src = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, backend_src)

try:
    from voice_interaction.voice_interaction import VoiceInteraction
except Exception as e:
    print('导入失败:', e)
    raise


async def main():
    vi = VoiceInteraction()

    # 指定测试音频（项目内的 zh.wav）作为输入
    zh = os.path.abspath(os.path.join(script_dir, '..', 'voice_interaction', 'zh.wav'))
    # 检查模型文件是否存在；若不存在则跳过 STT 测试以避免报错
    tokens_path = os.path.abspath(os.path.join(backend_src, 'voice_interaction', 'models',
                                               'sherpa-onnx-streaming-paraformer-bilingual-zh-en',
                                               'tokens.txt'))
    if os.path.exists(zh) and os.path.exists(tokens_path):
        vi.speech_recognizer.audio_path = zh
        try:
            print('开始异步 STT...')
            res = await vi.stt_async()
            print('STT 返回:', res)
        except Exception as e:
            print('STT 失败:', e)
    else:
        print('缺少模型文件或测试音频，跳过 STT:')
        print('  音频:', zh, os.path.exists(zh))
        print('  tokens:', tokens_path, os.path.exists(tokens_path))

    # 设置 TTS 输出到可写的临时目录
    outdir = os.path.join(script_dir, 'tmp_output')
    os.makedirs(outdir, exist_ok=True)
    vi.text_to_speech.output_path = outdir
    try:
        print('开始异步 TTS...')
        path = await vi.tts_async('测试异步 TTS', output='test_out.wav')
        print('TTS 生成文件路径:', path)
        print('文件存在:', os.path.exists(path))
    except Exception as e:
        print('TTS 失败:', e)


if __name__ == '__main__':
    asyncio.run(main())
