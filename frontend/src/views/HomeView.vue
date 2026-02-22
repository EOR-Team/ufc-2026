<template>
  <FixedAspectContainer
    bg-color-class="bg-white dark:bg-slate-900"
    extra-class="font-display text-slate-900 dark:text-slate-100"
    :shadow="true"
    :overflow-hidden="false"
  >
    <!-- 顶部标题栏 -->
    <header class="flex items-center pt-11 pb-8 px-6 justify-center">
      <p class="text-3xl tracking-tight text-slate-900 dark:text-white">登录</p>
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
        <div class="absolute inset-0 flex items-center justify-center overflow-hidden rounded-3xl bg-white dark:bg-slate-900 shadow-xl border border-slate-200 dark:border-slate-800">
          <!-- 模拟扫描图形 -->
          <div class="relative w-full h-full flex items-center justify-center">
            <span class="material-symbols-outlined text-[160px] text-primary/10 select-none">face</span>

            <!-- 科技覆盖层 -->
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-48 h-48 border-2 border-dashed border-primary/40 rounded-full"></div>
              <div class="absolute h-1 bg-primary/40 blur-sm top-1/2 -translate-y-1/2 w-full"></div>
            </div>

            <!-- 扫描点 -->
            <div class="absolute top-1/4 left-1/3 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-1"></div>
            <div class="absolute top-1/3 right-1/4 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-2"></div>
            <div class="absolute bottom-1/3 left-1/4 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-3"></div>
            <div class="absolute bottom-1/4 right-1/2 w-2 h-2 bg-primary rounded-full glow-effect chaos-motion-4"></div>

            <!-- 扫描线覆盖层 -->
            <div class="scan-line top-1/4 opacity-50"></div>
          </div>
        </div>

        <!-- 角标装饰 -->
        <div class="absolute -top-2 -left-2 w-8 h-8 border-t-4 border-l-4 border-primary rounded-tl-lg"></div>
        <div class="absolute -top-2 -right-2 w-8 h-8 border-t-4 border-r-4 border-primary rounded-tr-lg"></div>
        <div class="absolute -bottom-2 -left-2 w-8 h-8 border-b-4 border-l-4 border-primary rounded-bl-lg"></div>
        <div class="absolute -bottom-2 -right-2 w-8 h-8 border-b-4 border-r-4 border-primary rounded-br-lg"></div>
      </div>

      <!-- 使用说明 -->
      <div class="text-center mb-8 space-y-2">
        <p class="text-slate-500 dark:text-slate-400 text-sm">请正对屏幕并保持环境光线充足</p>
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
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-transparent dark:bg-transparent rounded-full">
        <span class="material-symbols-outlined text-primary text-sm">verified_user</span>
        <span class="text-xs text-slate-500 dark:text-slate-400 font-medium tracking-wide uppercase">AI 安全加密保护</span>
      </div>
    </footer>
  </FixedAspectContainer>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'

const router = useRouter()
const isLoggingIn = ref(false)

const handleFaceLogin = async () => {
  if (isLoggingIn.value) return
  
  isLoggingIn.value = true
  
  try {
    // 模拟人脸识别过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 登录成功后跳转到聊天页面
    router.push({ name: 'chat' })
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