<script setup>
/**
 * AppBottomNav — 底部导航栏（含中央 FAB 麦克风按钮）
 *
 * Props:
 *   isListening (boolean) — 是否处于语音监听状态（控制 FAB 样式）
 *
 * Emits:
 *   press-start — 用户开始按下 FAB 时触发
 *   press-end   — 用户松开或移出 FAB 时触发
 */
import { useRouter, useRoute } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const route = useRoute()

// 触摸移动检测
const touchStartY = ref(0)
const TOUCH_MOVE_THRESHOLD = 30 // 像素（增加阈值，避免轻微移动取消长按）


const props = defineProps({
  isListening: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['press-start', 'press-end'])

const onPressStart = () => {
  emit('press-start')
}
const onPressEnd = () => {
  // 重置触摸起始位置
  touchStartY.value = 0
  emit('press-end')
}

/** 触摸开始处理 */
const onTouchStart = (e) => {
  // 阻止默认行为，避免滚动干扰长按
  e.preventDefault()
  // 记录起始位置
  if (e.touches && e.touches.length > 0) {
    touchStartY.value = e.touches[0].clientY
  }
  onPressStart()
}

/** 触摸移动处理 */
const onTouchMove = (e) => {
  const currentY = e.touches && e.touches.length > 0 ? e.touches[0].clientY : 0

  if (!touchStartY.value || !e.touches || e.touches.length === 0) return

  const deltaY = Math.abs(currentY - touchStartY.value)

  // 如果垂直移动超过阈值，可以取消长按（当前禁用）
  if (deltaY > TOUCH_MOVE_THRESHOLD) {
    // 可以在这里取消长按：onPressEnd()
  }
}

/** 阻止短按 click 事件干扰长按逻辑 */
const preventClick = (e) => e.preventDefault()
</script>

<template>
  <nav class="relative bg-white border-t border-primary/10 px-3 py-2 flex items-center justify-between z-40">

    <!-- 智能寻路 -->
    <div
      class="flex flex-col items-center gap-1 flex-1 cursor-pointer"
      :class="route.path === '/nav_page' ? 'opacity-100' : 'opacity-50 hover:opacity-75'"
      @click="router.push('/nav_page')"
    >
      <span
        class="material-symbols-outlined"
        :class="route.path === '/nav_page' ? 'text-primary' : 'text-slate-500'"
      >map</span>
      <span
        class="text-[10px] font-medium"
        :class="route.path === '/nav_page' ? 'text-primary' : 'text-slate-500'"
      >智能寻路</span>
    </div>

    <!-- Center FAB -->
    <div class="relative flex-1 flex justify-center">
      <div class="absolute -top-16">
        <button
          class="relative flex flex-col items-center justify-center w-20 h-20 rounded-full text-white shadow-[0_8px_20px_rgba(0,0,0,0.35)] active:scale-95 z-10 border-4 border-white bg-primary hover:shadow-[0_12px_28px_rgba(0,0,0,0.45)]"
          style="border-radius: 9999px; touch-action: none;"
          @mousedown="onPressStart"
          @touchstart="onTouchStart"
          @mouseup="onPressEnd"
          @touchend="onPressEnd"
          @touchmove="onTouchMove"
          @click="preventClick"
          :class="{
            'scale-95 bg-primary/90 !shadow-[0_16px_32px_rgba(0,0,0,0.55)]': isListening
          }"
        >
          <span
            class="material-symbols-outlined text-3xl mb-1"
            :style="{
              'font-variation-settings': isListening ? '\'FILL\' 1, \'wght\' 700' : '\'FILL\' 1'
            }"
          >
            mic
          </span>
          <span class="text-[10px] font-medium text-white/90 opacity-90 tracking-tight select-none">
            长按说话
          </span>
        </button>
      </div>
    </div>

    <!-- 智能医患 -->
    <div
      class="flex flex-col items-center gap-1 flex-1 cursor-pointer"
      :class="route.path === '/doctor_page' ? 'opacity-100' : 'opacity-50 hover:opacity-75'"
      @click="router.push('/doctor_page')"
    >
      <span
        class="material-symbols-outlined"
        :class="route.path === '/doctor_page' ? 'text-primary' : 'text-slate-500'"
      >medical_services</span>
      <span
        class="text-[10px] font-medium"
        :class="route.path === '/doctor_page' ? 'text-primary' : 'text-slate-500'"
      >智能医患</span>
    </div>

  </nav>
</template>
