import { ref, onUnmounted } from 'vue'

/**
 * 语音录制 Composable
 *
 * 提供语音录制功能，与 useLongPress 集成使用。
 * 支持开始录音、停止录音、获取音频 Blob，并处理浏览器权限和错误。
 *
 * @returns {Object} Voice recorder API
 * @property {Ref<boolean>} isRecording - 是否正在录音
 * @property {Ref<boolean>} hasPermission - 是否有麦克风权限
 * @property {Ref<string|null>} error - 错误信息
 * @property {Function} startRecording - 开始录音
 * @property {Function} stopRecording - 停止录音并返回音频 Blob
 * @property {Function} requestPermission - 请求麦克风权限
 * @property {Function} cleanup - 清理资源
 */
export function useVoiceRecorder() {
  // 状态
  const isRecording = ref(false)
  const hasPermission = ref(false)
  const error = ref(null)

  // 录音相关变量
  let mediaStream = null
  let mediaRecorder = null
  let audioChunks = []

  /**
   * 请求麦克风权限
   * @returns {Promise<boolean>} 是否获得权限
   */
  const requestPermission = async () => {
    try {
      error.value = null

      // 检查浏览器支持
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('您的浏览器不支持语音录制功能')
      }

      // 请求麦克风权限
      const constraints = {
        audio: {
          channelCount: 1, // 单声道
          sampleRate: 16000, // 16kHz，符合后端推荐
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      }

      mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
      hasPermission.value = true
      console.log('[VoiceRecorder] 麦克风权限获取成功')
      return true
    } catch (err) {
      error.value = `麦克风权限获取失败: ${err.message}`
      console.error('[VoiceRecorder] 权限获取失败:', err)
      hasPermission.value = false
      return false
    }
  }

  /**
   * 开始录音
   * @returns {Promise<boolean>} 是否成功开始录音
   */
  const startRecording = async () => {
    try {
      error.value = null
      audioChunks = []

      // 如果没有权限，先请求权限
      if (!hasPermission.value) {
        const granted = await requestPermission()
        if (!granted) {
          return false
        }
      }

      // 检查 MediaRecorder 支持
      if (!MediaRecorder) {
        throw new Error('您的浏览器不支持 MediaRecorder API')
      }

      // 创建 MediaRecorder 实例
      // 优先尝试 WAV 格式，如果不支持则使用浏览器默认格式
      const mimeTypes = [
        'audio/wav',
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        ''
      ]

      let selectedMimeType = ''
      for (const mimeType of mimeTypes) {
        if (mimeType === '' || MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType
          break
        }
      }

      console.log('[VoiceRecorder] 使用音频格式:', selectedMimeType || '浏览器默认格式')

      const options = selectedMimeType ? { mimeType: selectedMimeType } : {}
      mediaRecorder = new MediaRecorder(mediaStream, options)

      // 设置数据可用时的处理
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data)
        }
      }

      // 设置录音错误处理
      mediaRecorder.onerror = (event) => {
        console.error('[VoiceRecorder] 录音错误:', event.error)
        error.value = `录音错误: ${event.error?.message || '未知错误'}`
        stopRecording()
      }

      // 开始录音
      mediaRecorder.start(100) // 每100ms收集一次数据
      isRecording.value = true
      console.log('[VoiceRecorder] 开始录音')

      return true
    } catch (err) {
      error.value = `开始录音失败: ${err.message}`
      console.error('[VoiceRecorder] 开始录音失败:', err)
      isRecording.value = false
      return false
    }
  }

  /**
   * 停止录音
   * @returns {Promise<Blob|null>} 音频 Blob 或 null（如果失败）
   */
  const stopRecording = () => {
    return new Promise((resolve) => {
      try {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') {
          console.warn('[VoiceRecorder] 录音器未启动或已停止')
          resolve(null)
          return
        }

        // 设置录音完成回调
        mediaRecorder.onstop = () => {
          isRecording.value = false

          if (audioChunks.length === 0) {
            console.warn('[VoiceRecorder] 未录制到音频数据')
            resolve(null)
            return
          }

          // 创建音频 Blob
          const mimeType = mediaRecorder.mimeType || 'audio/webm'
          const audioBlob = new Blob(audioChunks, { type: mimeType })

          console.log(`[VoiceRecorder] 录音完成，大小: ${audioBlob.size} 字节，格式: ${mimeType}`)
          resolve(audioBlob)
        }

        // 停止录音
        mediaRecorder.stop()
        console.log('[VoiceRecorder] 停止录音')

      } catch (err) {
        error.value = `停止录音失败: ${err.message}`
        console.error('[VoiceRecorder] 停止录音失败:', err)
        isRecording.value = false
        resolve(null)
      }
    })
  }

  /**
   * 清理资源
   */
  const cleanup = () => {
    // 停止录音
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      try {
        mediaRecorder.stop()
      } catch (err) {
        console.warn('[VoiceRecorder] 清理时停止录音失败:', err)
      }
    }

    // 停止媒体流
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }

    // 重置状态
    isRecording.value = false
    mediaRecorder = null
    audioChunks = []

    console.log('[VoiceRecorder] 资源已清理')
  }

  // 组件卸载时自动清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    // 状态
    isRecording,
    hasPermission,
    error,

    // 方法
    requestPermission,
    startRecording,
    stopRecording,
    cleanup
  }
}