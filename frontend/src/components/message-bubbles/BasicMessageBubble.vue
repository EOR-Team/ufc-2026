<script setup>
import { computed } from 'vue'

const props = defineProps({
  /**
   * 消息内容
   */
  message: {
    type: String,
    required: true
  },
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
  }
})

// 计算气泡的最大宽度（固定为80%）
const maxWidthStyle = computed(() => {
  return 'max-width: 80%'
})

// 根据是否为助手消息决定布局类
const layoutClasses = computed(() => {
  return props.isAssistant 
    ? 'flex items-start gap-3' 
    : 'flex items-start gap-3 flex-row-reverse'
})

// 根据是否为助手消息决定气泡圆角类
const bubbleClasses = computed(() => {
  return props.isAssistant
    ? 'bg-primary/10 text-slate-800 px-3 py-2 rounded-xl rounded-tl-none shadow-sm'
    : 'bg-slate-100 text-slate-800 px-3 py-2 rounded-xl rounded-tr-none shadow-sm'
})

// 根据是否为助手消息决定名称标签对齐
const nameLabelClasses = computed(() => {
  return props.isAssistant
    ? 'text-xs font-medium text-slate-500 uppercase tracking-wider ml-1'
    : 'text-xs font-medium text-slate-500 uppercase tracking-wider mr-1 text-right'
})
</script>

<template>
  <div :class="layoutClasses" class="mt-2 mb-2 ml-3 mr-3">
    <!-- 图标 -->
    <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
      <span class="material-symbols-outlined text-primary">
        {{ icon }}
      </span>
    </div>

    <!-- 消息内容区域 -->
    <div class="flex flex-col gap-1" :style="maxWidthStyle">
      <!-- 名称标签 -->
      <div :class="nameLabelClasses">
        {{ name }}
      </div>

      <!-- 消息气泡 -->
      <div :class="bubbleClasses">
        <p class="text-base leading-relaxed m-0">
          {{ message }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 确保气泡文本不会溢出 */
p {
  word-break: break-word;
  overflow-wrap: break-word;
}
</style>