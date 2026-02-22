<script setup>
import { ref, onMounted, onUpdated, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import MessageBubble from '@/components/message-bubbles'
import ListeningIndicator from '@/components/ListeningIndicator.vue'

const router = useRouter()

// 控制ListeningIndicator显示/隐藏的状态
const isListening = ref(false)

// 长按计时器引用
let longPressTimer = null
const LONG_PRESS_DURATION = 250 // 长按持续时间（毫秒）

// 智能居中状态
const contentExceedsViewport = ref(false)

// 消息列表
const messages = ref([
  {
    name: "assistant",
    message: "你好！今天有什么我可以帮你的吗？"
  },
  {
    name: "user",
    message: "我想去门诊部"
  },
  {
    name: "assistant",
    message: "好的，我可以帮你导航到门诊部。请问你现在在哪里？"
  },
  {
    name: "user",
    message: "我在医院大厅"
  },
  {
    name: "assistant",
    message: "明白了。从医院大厅到门诊部，你可以按照以下路线：\n\n1. 从医院大厅出发，向东走，经过咖啡厅。\n2. 继续直行，经过电梯和休息区。\n3. 在第一个路口右转，进入主走廊。\n4. 沿着主走廊一直走，直到看到门诊部的标志。\n\n如果你需要更详细的指引或者有任何问题，请随时告诉我！"
  }
])

// 检测内容是否超出视口
const checkContentHeight = () => {
  nextTick(() => {
    const mainDisplayBlock = document.getElementById('main-display-block')
    const contentContainer = document.querySelector('.flex-1.min-h-0')
    
    if (mainDisplayBlock && contentContainer) {
      const containerHeight = mainDisplayBlock.clientHeight
      const contentHeight = contentContainer.scrollHeight
      
      // 如果内容高度大于容器高度，则切换到顶部对齐
      contentExceedsViewport.value = contentHeight > containerHeight
      
      // 根据条件添加或移除类名
      if (contentExceedsViewport.value) {
        mainDisplayBlock.classList.add('content-exceeds-viewport')
      } else {
        mainDisplayBlock.classList.remove('content-exceeds-viewport')
      }
    }
  })
}

// 在组件挂载和更新时检测
onMounted(() => {
  checkContentHeight()
  // 监听窗口大小变化
  window.addEventListener('resize', checkContentHeight)
})

onUpdated(() => {
  checkContentHeight()
})

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
    <header class="flex items-center bg-white px-3 py-3 justify-between border-b sticky top-0 z-40 border-primary/20">
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
    <div class="flex-1 flex flex-col relative min-h-0"> <!-- 添加 min-h-0 防止flex子元素溢出 -->
      <!-- Conversation History - Takes all available height with proper scrolling -->
      <div class="flex-1 overflow-y-auto no-scrollbar min-h-0" style="padding: 12px;">
        <div class="flex flex-col gap-3">
          <MessageBubble
            v-for="(msg, index) in messages"
            :key="index"
            :name="msg.name"
            :message="msg.message"
          />
        </div>
      </div>

      <!-- Blur Layer - sits between content and ListeningIndicator -->
      <Transition name="blur-fade">
        <div
          v-if="isListening"
          class="blur-layer absolute inset-0 pointer-events-none z-20"
        />
      </Transition>

      <!-- Listening Indicator - Floating overlay with transparent background -->
      <Transition name="fade">
        <div 
          v-if="isListening"
          class="absolute inset-0 pointer-events-none flex items-center justify-center bg-transparent z-30"
        >
          <ListeningIndicator />
        </div>
      </Transition>
    </div>

    <!-- Bottom Navigation -->
    <nav class="relative bg-white border-t border-primary/10 px-3 py-3 flex items-center justify-between z-40">
      <!-- 智能寻路 -->
      <div class="flex flex-col items-center gap-1 flex-1 cursor-pointer hover:opacity-80 transition-opacity">
        <span class="material-symbols-outlined text-slate-500">map</span>
        <span class="text-[10px] font-medium text-slate-500">智能寻路</span>
      </div>
      <!-- Center FAB -->
      <div class="relative flex-1 flex justify-center">
        <div class="absolute -top-14">
          <div class="relative flex items-center justify-center">
            <button 
              class="relative flex flex-col items-center justify-center w-20 h-20 rounded-full text-white shadow-[0_8px_20px_rgba(0,0,0,0.35)] active:scale-95 transition-all z-10 border-4 border-white bg-primary hover:shadow-[0_12px_28px_rgba(0,0,0,0.45)]"
              style="border-radius: 9999px;"
              @mousedown="startLongPress"
              @touchstart="startLongPress"
              @mouseup="endLongPress"
              @touchend="endLongPress"
              @mouseleave="endLongPress"
              @click="preventClick"
              :class="{ 
                'scale-95 bg-primary/90 shadow-[0_16px_32px_rgba(0,0,0,0.55)]!': isListening
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
/* Blur layer */
.blur-layer {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

/* Fade transition for ListeningIndicator overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Blur-fade transition for blur-layer */
.blur-fade-enter-active,
.blur-fade-leave-active {
  transition: opacity 0.25s ease;
}
.blur-fade-enter-from,
.blur-fade-leave-to {
  opacity: 0;
}

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

/* 智能居中逻辑 */
.content-exceeds-viewport {
  align-items: flex-start !important;
}
</style>
