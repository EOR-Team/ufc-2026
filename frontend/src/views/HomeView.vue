<template>
  <FixedAspectContainer
    bg-color-class="bg-white"
    extra-class="font-display text-slate-900"
    :shadow="true"
    :overflow-hidden="false"
  >
    <!-- 顶部标题栏 -->
    <header class="flex items-center pt-11 pb-8 px-6 justify-center">
      <p class="text-3xl tracking-tight text-slate-900">登录</p>
    </header>

    <!-- 主内容区 -->
    <main class="flex-1 flex flex-col items-center justify-center px-6 max-w-md mx-auto w-full">
      <!-- 生物识别可视化区域 -->
      <div class="relative w-full aspect-square max-w-[320px] mb-8 group">
        <!-- 装饰性背景环 -->
        <div class="absolute inset-0 rounded-full border-2 border-primary/10 animate-pulse"></div>
        <div class="absolute inset-8 rounded-full border border-primary/20"></div>
        <div class="absolute inset-16 rounded-full border border-primary/30"></div>

        <!-- 主插画容器 -->
        <div class="absolute inset-0 flex items-center justify-center overflow-hidden rounded-3xl bg-white shadow-xl border border-slate-200">
          <!-- 摄像头画面（有摄像头时显示） -->
          <video
            v-show="permissionState === 'granted' && cameraCount > 0"
            ref="videoRef"
            autoplay
            playsinline
            muted
            class="absolute inset-0 w-full h-full object-cover scale-x-[-1]"
          />

          <!-- 无摄像头时的占位图形 -->
          <div v-if="permissionState !== 'granted' || cameraCount <= 0" class="relative w-full h-full flex items-center justify-center">
            <span class="material-symbols-outlined text-[160px] text-primary/10 select-none">face</span>
          </div>

          <!-- 科技覆盖层（始终叠加在摄像头上方） -->
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div class="w-48 h-48 border-2 border-dashed border-primary/40 rounded-full"></div>
            <div class="absolute h-1 bg-primary/40 blur-sm top-1/2 -translate-y-1/2 w-full"></div>
          </div>

          <!-- 扫描点 -->
          <div class="absolute top-1/4 left-1/3 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-1 pointer-events-none"></div>
          <div class="absolute top-1/3 right-1/4 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-2 pointer-events-none"></div>
          <div class="absolute bottom-1/3 left-1/4 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-3 pointer-events-none"></div>
          <div class="absolute bottom-1/4 right-1/2 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-4 pointer-events-none"></div>

          <!-- 扫描线覆盖层 -->
          <div class="scan-line top-1/4 opacity-50 pointer-events-none"></div>

          <!-- 错误提示 -->
          <div v-if="error" class="absolute bottom-2 left-0 right-0 text-center text-[10px] text-red-400 px-2">{{ error }}</div>

          <!-- 摄像头权限按钮 -->
          <button
            v-if="showCameraPermissionButton"
            @click="handleCameraPermissionClick"
            class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-40 flex items-center justify-center w-16 h-16 bg-primary/90 hover:bg-primary rounded-full shadow-lg transition-all active:scale-95"
            :class="{
              'bg-red-500/90 hover:bg-red-600': permissionState === 'denied',
              'cursor-not-allowed opacity-75': isCheckingPermission
            }"
            :disabled="isCheckingPermission"
          >
            <span class="material-symbols-outlined text-white text-2xl">
              {{ permissionState === 'denied' ? 'warning' : 'videocam' }}
            </span>
          </button>
        </div>

        <!-- 角标装饰 -->
        <div class="absolute -top-2 -left-2 w-8 h-8 border-t-4 border-l-4 border-primary rounded-tl-lg"></div>
        <div class="absolute -top-2 -right-2 w-8 h-8 border-t-4 border-r-4 border-primary rounded-tr-lg"></div>
        <div class="absolute -bottom-2 -left-2 w-8 h-8 border-b-4 border-l-4 border-primary rounded-bl-lg"></div>
        <div class="absolute -bottom-2 -right-2 w-8 h-8 border-b-4 border-r-4 border-primary rounded-br-lg"></div>
      </div>

      <!-- 使用说明 -->
      <div class="text-center mb-8 space-y-2">
        <p class="text-slate-500 text-sm">请正对屏幕并保持环境光线充足</p>
      </div>

      <!-- 操作按钮 -->
      <div class="w-full space-y-4">
        <button 
          @click="handleFaceLogin"
          class="w-full bg-primary hover:bg-primary/90 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/25 transition-all active:scale-[0.98] flex items-center justify-center gap-3"
          :disabled="isLoggingIn"
          :class="{ 'opacity-75 cursor-not-allowed': isLoggingIn }"
        >
          <span class="material-symbols-outlined">face_unlock</span>
          <span>{{ isLoggingIn ? '正在识别...' : '使用人脸登录' }}</span>
        </button>
      </div>
    </main>

    <!-- 底部安全徽章 -->
    <footer class="p-8 mb-6 text-center">
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-transparent rounded-full">
        <span class="material-symbols-outlined text-primary text-sm">verified_user</span>
        <span class="text-xs text-slate-500 font-medium tracking-wide uppercase">AI 安全加密保护</span>
      </div>
    </footer>
  </FixedAspectContainer>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import { useCamera } from '@/composables/useCamera'

const router = useRouter()
const isLoggingIn = ref(false)

const { videoRef, cameraCount, error, start, permissionState, requestPermission, queryCameraPermission, setupPermissionListener } = useCamera()
const isCheckingPermission = ref(false)

// 页面加载时初始化权限状态
onMounted(async () => {
  // 查询初始权限状态
  const state = await queryCameraPermission()
  permissionState.value = state

  // 设置权限状态监听
  setupPermissionListener()

  // 如果已有权限，自动启动摄像头
  if (permissionState.value === 'granted') {
    await start()
  }
})

// 计算是否显示权限按钮
const showCameraPermissionButton = computed(() => {
  return permissionState.value !== 'granted'
})

// 按钮点击处理
const handleCameraPermissionClick = async () => {
  if (permissionState.value === 'denied') {
    // 显示详细的权限恢复指引
    showPermissionDeniedAlert()
    return
  }

  // prompt状态：请求权限
  isCheckingPermission.value = true
  try {
    const granted = await requestPermission()
    if (granted) {
      // 权限获取成功，启动摄像头
      await start()
    }
  } finally {
    isCheckingPermission.value = false
  }
}

// 权限被拒绝时的alert提示
const showPermissionDeniedAlert = () => {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
  let message = '摄像头权限已被拒绝。\n\n'

  if (isMobile) {
    message += '请在系统设置中启用：\n'
    message += '1. 打开手机设置\n'
    message += '2. 找到浏览器应用\n'
    message += '3. 启用摄像头权限'
  } else {
    message += '请在浏览器设置中启用：\n'
    message += '1. 点击地址栏左侧锁形图标\n'
    message += '2. 选择"网站设置"\n'
    message += '3. 找到"摄像头"选项\n'
    message += '4. 更改为"允许"'
  }

  alert(message)
}

const handleFaceLogin = async () => {
  if (isLoggingIn.value) return
  
  isLoggingIn.value = true
  
  try {
    // 模拟人脸识别过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 登录成功后跳转到智能寻路页面
    router.push({ name: 'navigation' })
  } catch (error) {
    console.error('登录失败:', error)
    // 这里可以添加错误处理逻辑
  } finally {
    isLoggingIn.value = false
  }
}
</script>

<style scoped>
/* 登录页面特定样式 */

/* 扫描线动画 */
.scan-line {
  background: linear-gradient(to bottom, transparent, #4252b3, transparent);
  height: 40px;
  width: 100%;
  position: absolute;
  z-index: 10;
  animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
  0% {
    top: 25%;
    opacity: 0.5;
  }
  50% {
    top: 75%;
    opacity: 0.8;
  }
  100% {
    top: 25%;
    opacity: 0.5;
  }
}

/* 混沌运动动画 - 小范围旋转混沌效果 */
.chaos-motion-1 {
  animation: 
    glow 2s ease-in-out infinite alternate,
    chaosOrbit1 3s ease-in-out infinite;
}

.chaos-motion-2 {
  animation: 
    glow 2s ease-in-out infinite alternate,
    chaosOrbit2 2.5s ease-in-out infinite;
}

.chaos-motion-3 {
  animation: 
    glow 2s ease-in-out infinite alternate,
    chaosOrbit3 4.5s ease-in-out infinite;
}

.chaos-motion-4 {
  animation: 
    glow 2s ease-in-out infinite alternate,
    chaosOrbit4 5s ease-in-out infinite;
}

@keyframes chaosOrbit1 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(4px, -6px) rotate(90deg);
  }
  50% {
    transform: translate(-3px, 5px) rotate(180deg);
  }
  75% {
    transform: translate(5px, -4px) rotate(270deg);
  }
}

@keyframes chaosOrbit2 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(-5px, 3px) rotate(-90deg);
  }
  50% {
    transform: translate(6px, -4px) rotate(-180deg);
  }
  75% {
    transform: translate(-4px, 5px) rotate(-270deg);
  }
}

@keyframes chaosOrbit3 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(3px, 4px) rotate(120deg);
  }
  50% {
    transform: translate(-4px, -3px) rotate(240deg);
  }
  75% {
    transform: translate(5px, 2px) rotate(360deg);
  }
}

@keyframes chaosOrbit4 {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(-2px, -5px) rotate(-120deg);
  }
  50% {
    transform: translate(4px, 3px) rotate(-240deg);
  }
  75% {
    transform: translate(-3px, -4px) rotate(-360deg);
  }
}

/* 发光效果 */
.glow-effect {
  box-shadow: 0 0 25px 5px rgba(66, 82, 179, 0.2);

  from {
    box-shadow: 0 0 25px 5px rgba(66, 82, 179, 0.2);
  }
  to {
    box-shadow: 0 0 35px 10px rgba(66, 82, 179, 0.4);
  }
}

/* 脉冲动画 */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>