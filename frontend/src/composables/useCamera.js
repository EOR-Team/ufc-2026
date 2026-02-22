import { ref, onUnmounted } from 'vue'

/**
 * 摄像头 Composable
 *
 * 调用流程：
 *  1. getUserMedia 触发权限弹窗，获取 stream
 *  2. 授权后 enumerateDevices 枚举实际摄像头数量
 *  3. 将 stream 绑定到外部传入的 <video> ref
 *
 * @returns {{
 *   videoRef: Ref<HTMLVideoElement|null>,
 *   cameraCount: Ref<number>,
 *   error: Ref<string|null>,
 *   start: () => Promise<void>,
 *   stop: () => void,
 * }}
 */
export function useCamera() {
  const videoRef = ref(null)
  const cameraCount = ref(-1) // -1 = 尚未检测
  const error = ref(null)

  let stream = null

  const stop = () => {
    if (stream) {
      stream.getTracks().forEach(t => t.stop())
      stream = null
    }
    if (videoRef.value) {
      videoRef.value.srcObject = null
    }
  }

  const start = async () => {
    error.value = null

    // 防御：非安全上下文（http）下 mediaDevices 不可用
    if (!navigator.mediaDevices?.getUserMedia) {
      error.value = '需要 HTTPS 才能访问摄像头'
      cameraCount.value = 0
      return
    }

    try {
      // ideal 而非 exact：桌面端不支持 facingMode 时忽略该约束，而非报错
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'user' } },
        audio: false,
      })

      // 授权后枚举摄像头数量
      const devices = await navigator.mediaDevices.enumerateDevices()
      const cameras = devices.filter(d => d.kind === 'videoinput')
      cameraCount.value = cameras.length

      if (cameraCount.value === 0) {
        // 没有摄像头，释放刚才申请的 stream
        stop()
        return
      }

      // 绑定到 <video> 元素
      if (videoRef.value) {
        videoRef.value.srcObject = stream
        await videoRef.value.play()
      }
    } catch (e) {
      error.value = e.message
      stop()
    }
  }

  onUnmounted(() => stop())

  return { videoRef, cameraCount, error, start, stop }
}
