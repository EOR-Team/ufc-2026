import { ref, onUnmounted, computed } from 'vue'

/**
 * 摄像头 Composable
 *
 * 调用流程：
 *  1. 查询浏览器摄像头权限状态（granted/prompt/denied）
 *  2. 用户手势触发权限请求（requestPermission）
 *  3. 授权后 getUserMedia 获取 stream
 *  4. enumerateDevices 枚举实际摄像头数量
 *  5. 将 stream 绑定到外部传入的 <video> ref
 *
 * @returns {{
 *   videoRef: Ref<HTMLVideoElement|null>,
 *   cameraCount: Ref<number>,
 *   error: Ref<string|null>,
 *   permissionState: Ref<string>, // 'granted' | 'denied' | 'prompt' | 'unsupported' | 'unknown'
 *   hasPermission: Ref<boolean>,
 *   start: () => Promise<void>,
 *   stop: () => void,
 *   requestPermission: () => Promise<boolean>,
 *   queryCameraPermission: () => Promise<string>,
 *   setupPermissionListener: () => void,
 * }}
 */
export function useCamera() {
  const videoRef = ref(null)
  const cameraCount = ref(-1) // -1 = 尚未检测
  const error = ref(null)
  const permissionState = ref('prompt') // 'granted' | 'denied' | 'prompt' | 'unsupported' | 'unknown'
  const hasPermission = computed(() => permissionState.value === 'granted')

  let stream = null

  /**
   * 浏览器兼容性检测
   * @returns {Object} 兼容性信息
   */
  const checkBrowserCompatibility = () => {
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent)
    const isAndroid = /Android/i.test(navigator.userAgent)

    return {
      isMobile: isIOS || isAndroid,
      isIOS,
      isAndroid,
      supportsPermissionsAPI: !!navigator.permissions?.query
    }
  }

  /**
   * 查询摄像头权限状态
   * @returns {Promise<string>} 权限状态字符串
   */
  const queryCameraPermission = async () => {
    // 特性检测：是否支持Permissions API
    if (!navigator.permissions?.query) {
      // 降级方案：尝试通过enumerateDevices检测权限
      if (!navigator.mediaDevices?.enumerateDevices) {
        return 'unsupported'
      }
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        const hasCameraAccess = devices.some(
          device => device.kind === 'videoinput' && device.deviceId !== ''
        )
        return hasCameraAccess ? 'granted' : 'prompt'
      } catch {
        return 'unknown'
      }
    }

    try {
      const permissionStatus = await navigator.permissions.query({ name: 'camera' })
      return permissionStatus.state
    } catch (error) {
      console.error('查询摄像头权限失败:', error)
      return 'unknown'
    }
  }

  /**
   * 设置权限状态监听
   */
  const setupPermissionListener = () => {
    if (!navigator.permissions?.query) return

    navigator.permissions.query({ name: 'camera' }).then((permissionStatus) => {
      permissionStatus.onchange = () => {
        permissionState.value = permissionStatus.state
      }
    })
  }

  /**
   * 用户手势触发的权限请求
   * @returns {Promise<boolean>} 是否获得权限
   */
  const requestPermission = async () => {
    // 检查当前状态
    if (permissionState.value === 'granted') return true
    if (permissionState.value === 'denied') return false

    try {
      // 请求摄像头权限
      const testStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'user' } },
        audio: false,
      })

      // 立即释放测试流（只需要权限）
      testStream.getTracks().forEach(track => track.stop())

      // 重新查询更新状态
      permissionState.value = await queryCameraPermission()
      return permissionState.value === 'granted'

    } catch (error) {
      // 错误处理
      permissionState.value = await queryCameraPermission()
      return false
    }
  }

  /**
   * 错误类型分类处理
   */
  const handleCameraError = (err) => {
    const errorName = err.name || 'UnknownError'

    switch (errorName) {
      case 'NotAllowedError':
        error.value = '摄像头权限被拒绝，请在浏览器设置中启用'
        permissionState.value = 'denied'
        break
      case 'NotFoundError':
        error.value = '未找到摄像头设备'
        cameraCount.value = 0
        break
      case 'NotReadableError':
        error.value = '摄像头无法访问，可能被其他应用占用'
        break
      case 'SecurityError':
        error.value = '需要HTTPS连接才能访问摄像头'
        break
      default:
        error.value = `摄像头错误: ${err.message || '未知错误'}`
    }
  }

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

    // 检查权限状态
    if (!hasPermission.value) {
      error.value = '请先授予摄像头权限'
      return
    }

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
      handleCameraError(e)
      stop()
    }
  }

  onUnmounted(() => stop())

  return {
    videoRef,
    cameraCount,
    error,
    permissionState,
    hasPermission,
    start,
    stop,
    requestPermission,
    queryCameraPermission,
    setupPermissionListener
  }
}
