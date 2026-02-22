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
import { useChatModeStore } from '@/stores/useChatModeStore'

const chatMode = useChatModeStore()

const props = defineProps({
  isListening: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['press-start', 'press-end'])

const onPressStart = () => emit('press-start')
const onPressEnd = () => emit('press-end')

/** 阻止短按 click 事件干扰长按逻辑 */
const preventClick = (e) => e.preventDefault()
</script>

<template>
  <nav class="relative bg-white border-t border-primary/10 px-3 py-2 flex items-center justify-between z-40">

    <!-- 智能寻路 -->
    <div
      class="flex flex-col items-center gap-1 flex-1 cursor-pointer transition-opacity"
      :class="chatMode.mode === 'navigation' ? 'opacity-100' : 'opacity-50 hover:opacity-75'"
      @click="chatMode.setMode('navigation')"
    >
      <span
        class="material-symbols-outlined transition-colors"
        :class="chatMode.mode === 'navigation' ? 'text-primary' : 'text-slate-500'"
      >map</span>
      <span
        class="text-[10px] font-medium transition-colors"
        :class="chatMode.mode === 'navigation' ? 'text-primary' : 'text-slate-500'"
      >智能寻路</span>
    </div>

    <!-- Center FAB -->
    <div class="relative flex-1 flex justify-center">
      <div class="absolute -top-16">
        <button
          class="relative flex flex-col items-center justify-center w-20 h-20 rounded-full text-white shadow-[0_8px_20px_rgba(0,0,0,0.35)] active:scale-95 transition-all z-10 border-4 border-white bg-primary hover:shadow-[0_12px_28px_rgba(0,0,0,0.45)]"
          style="border-radius: 9999px;"
          @mousedown="onPressStart"
          @touchstart="onPressStart"
          @mouseup="onPressEnd"
          @touchend="onPressEnd"
          @mouseleave="onPressEnd"
          @click="preventClick"
          :class="{
            'scale-95 bg-primary/90 !shadow-[0_16px_32px_rgba(0,0,0,0.55)]': isListening
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
          <span class="text-[10px] font-medium text-white/90 opacity-90 tracking-tight select-none">
            长按说话
          </span>
        </button>
      </div>
    </div>

    <!-- 智能医患 -->
    <div
      class="flex flex-col items-center gap-1 flex-1 cursor-pointer transition-opacity"
      :class="chatMode.mode === 'medical' ? 'opacity-100' : 'opacity-50 hover:opacity-75'"
      @click="chatMode.setMode('medical')"
    >
      <span
        class="material-symbols-outlined transition-colors"
        :class="chatMode.mode === 'medical' ? 'text-primary' : 'text-slate-500'"
      >medical_services</span>
      <span
        class="text-[10px] font-medium transition-colors"
        :class="chatMode.mode === 'medical' ? 'text-primary' : 'text-slate-500'"
      >智能医患</span>
    </div>

  </nav>
</template>
