<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AssistantMessageBubble from '@/components/AssistantMessageBubble.vue'
import UserMessageBubble from '@/components/UserMessageBubble.vue'
import ListeningIndicator from '@/components/ListeningIndicator.vue'

const router = useRouter()

// 控制ListeningIndicator显示/隐藏的状态
const isListening = ref(false)

// 长按计时器引用
let longPressTimer = null
const LONG_PRESS_DURATION = 350 // 长按持续时间（毫秒）

// 开始长按
const startLongPress = () => {
  longPressTimer = setTimeout(() => {
    isListening.value = true
  }, LONG_PRESS_DURATION)
}

// 结束长按
const endLongPress = () => {
  if (longPressTimer) {
    clearTimeout(longPressTimer)
    longPressTimer = null
  }
  isListening.value = false
}

// 防止按钮的默认点击行为干扰长按
const preventClick = (event) => {
  event.preventDefault()
}
</script>

<template>
  <FixedAspectContainer 
    width="332"
    :height="774.66"
    bg-color-class="bg-white"
    extra-class="font-display"
  >

    <!-- TopAppBar -->
    <header class="flex items-center bg-white px-3 py-3 justify-between border-b sticky top-0 z-10 border-primary/20">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white">
          <span class="material-symbols-outlined" style="font-size:18px">graphic_eq</span>
        </div>
        <p class="text-slate-900 text-xl font-semibold tracking-tight m-0">语音助手</p>
      </div>
      <button
        @click="router.push({ name: 'settings' })"
        class="flex items-center justify-center rounded-full w-10 h-10 hover:bg-primary/10 transition-colors text-slate-600"
      >
        <span class="material-symbols-outlined">settings</span>
      </button>
    </header>

    <!-- Main Content Area - Fills space between TopAppBar and Bottom Navigation -->
    <div class="flex-1 flex flex-col relative">
      <!-- Conversation History - Takes all available height -->
      <div class="flex-1 overflow-y-auto no-scrollbar" style="padding: 12px;">
        <div class="flex flex-col gap-3">
          <AssistantMessageBubble
            message="你好！今天有什么我可以帮你的吗？"
          />
          <UserMessageBubble
            message="我想去门诊部"
          />
          <AssistantMessageBubble
            message="好的，我为您规划去门诊部的路线。请稍等..."
            name="导航助手"
            icon="directions"
          />
        </div>
      </div>

      <!-- Listening Indicator - Floating overlay with transparent background -->
      <div 
        v-if="isListening"
        class="absolute inset-0 pointer-events-none flex items-center justify-center bg-transparent z-20"
      >
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
          <ListeningIndicator />
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <nav class="relative bg-white border-t border-primary/10 px-3 py-3 flex items-center justify-between">
      <!-- 智能寻路 -->
      <div class="flex flex-col items-center gap-1 flex-1 cursor-pointer hover:opacity-80 transition-opacity">
        <span class="material-symbols-outlined text-slate-500">map</span>
        <span class="text-[10px] font-medium text-slate-500">智能寻路</span>
      </div>
      <!-- Center FAB -->
      <div class="relative flex-1 flex justify-center">
        <div class="absolute -top-10">
          <div class="relative flex items-center justify-center">
            <button 
              class="relative flex flex-col items-center justify-center w-20 h-20 rounded-full text-white shadow-[0_10px_25px_rgba(0,0,0,0.3)] active:scale-95 transition-all z-10 border-4 border-white bg-primary hover:shadow-[0_15px_35px_rgba(0,0,0,0.4)]"
              style="border-radius: 9999px;"
              @mousedown="startLongPress"
              @touchstart="startLongPress"
              @mouseup="endLongPress"
              @touchend="endLongPress"
              @mouseleave="endLongPress"
              @click="preventClick"
              :class="{ 
                'scale-95 bg-primary/90 !shadow-[0_20px_40px_rgba(0,0,0,0.5)]': isListening
              }"
            >
              <span 
                class="material-symbols-outlined text-3xl transition-all mb-1"
                :style="{ 
                  'font-variation-settings': isListening ? '\'FILL\' 1, \'wght\' 700' : '\'FILL\' 1'
                }"
              >
                mic
              </span>
              <!-- 长按提示 - 嵌入到按钮内部 -->
              <span class="text-[10px] font-medium text-white/90 opacity-90 tracking-tight">
                长按说话
              </span>
            </button>
          </div>
        </div>
      </div>
      <!-- 智能医患 -->
      <div class="flex flex-col items-center gap-1 flex-1 cursor-pointer hover:opacity-80 transition-opacity">
        <span class="material-symbols-outlined text-slate-500">medical_services</span>
        <span class="text-[10px] font-medium text-slate-500">智能医患</span>
      </div>
    </nav>
    <div class="h-3 bg-white"></div>

  </FixedAspectContainer>
</template>

<style scoped>
@keyframes pulse-ring {
  0%   { transform: scale(0.8); opacity: 0.5; }
  50%  { transform: scale(1.2); opacity: 0.3; }
  100% { transform: scale(0.8); opacity: 0.5; }
}
@keyframes wave-flow {
  0%   { height: 20px; }
  50%  { height: 80px; }
  100% { height: 20px; }
}
.animate-pulse-ring {
  animation: pulse-ring 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.animate-wave-1 { animation: wave-flow 1.2s ease-in-out infinite; }
.animate-wave-2 { animation: wave-flow 1.5s ease-in-out infinite; animation-delay: 0.2s; }
.animate-wave-3 { animation: wave-flow 1.0s ease-in-out infinite; animation-delay: 0.4s; }
.animate-wave-4 { animation: wave-flow 1.8s ease-in-out infinite; animation-delay: 0.1s; }
.animate-wave-5 { animation: wave-flow 1.3s ease-in-out infinite; animation-delay: 0.3s; }
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
