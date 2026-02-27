<script setup>
import { computed } from 'vue'

const props = defineProps({
  /**
   * 发送者名称
   */
  name: {
    type: String,
    required: true
  },
  /**
   * 图标名称（Material Symbols）
   */
  icon: {
    type: String,
    required: true
  },
  /**
   * 是否为助手消息（决定布局方向）
   */
  isAssistant: {
    type: Boolean,
    default: true
  },
  /**
   * 骨架屏类型（影响动画样式）
   * - 'blinking': 闪烁动画（默认）
   * - 'wave': 波浪动画
   * - 'pulse': 脉冲动画
   */
  animationType: {
    type: String,
    default: 'blinking',
    validator: (value) => ['blinking', 'wave', 'pulse'].includes(value)
  }
})

// 计算气泡的最大宽度（固定为80%）
const maxWidthStyle = computed(() => {
  return 'max-width: 80%'
})

// 根据是否为助手消息决定布局类
const layoutClasses = computed(() => {
  return props.isAssistant
    ? 'flex-row items-start gap-3'
    : 'flex-row-reverse items-start gap-3'
})

// 根据是否为助手消息决定气泡颜色类
const bubbleColorClasses = computed(() => {
  return props.isAssistant
    ? 'bg-primary-50 border border-primary-100'
    : 'bg-gray-100 border border-gray-200'
})

// 根据动画类型决定动画类
const animationClasses = computed(() => {
  switch (props.animationType) {
    case 'blinking':
      return 'animate-pulse'
    case 'wave':
      return 'animate-wave'
    case 'pulse':
      return 'animate-pulse-slow'
    default:
      return 'animate-pulse'
  }
})
</script>

<template>
  <div class="flex" :class="layoutClasses">
    <!-- 头像/图标容器 -->
    <div class="flex-shrink-0">
      <div
        class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center"
        :class="animationClasses"
      >
        <span class="material-symbols-outlined text-gray-400 text-lg">
          {{ icon }}
        </span>
      </div>
    </div>

    <!-- 消息气泡容器 -->
    <div class="flex flex-col gap-2 flex-1" :style="maxWidthStyle">
      <!-- 发送者名称 -->
      <div class="flex items-center gap-2">
        <div
          class="h-4 rounded-full bg-gray-200"
          :class="[animationClasses, isAssistant ? 'w-16' : 'w-12']"
        />
      </div>

      <!-- 骨架屏消息内容 -->
      <div
        class="rounded-2xl px-4 py-3"
        :class="[bubbleColorClasses, animationClasses]"
      >
        <!-- 多行骨架文本 -->
        <div class="space-y-2">
          <div class="h-3 rounded-full bg-gray-300/50 w-full"></div>
          <div class="h-3 rounded-full bg-gray-300/50 w-3/4"></div>
          <div class="h-3 rounded-full bg-gray-300/50 w-5/6"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes wave {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

.animate-pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.animate-wave {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: wave 1.5s ease-in-out infinite;
}
</style>