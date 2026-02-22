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
  }
})

// 计算气泡的最大宽度（固定为80%）
const maxWidthStyle = computed(() => {
  return 'max-width: 80%'
})
</script>

<template>
  <div class="flex items-start gap-3 mt-2 mb-2 ml-3 mr-3">
    <!-- 图标 -->
    <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
      <span class="material-symbols-outlined text-primary">
        {{ icon }}
      </span>
    </div>

    <!-- 消息内容区域 -->
    <div class="flex flex-col gap-1" :style="maxWidthStyle">
      <!-- 名称标签 -->
      <div class="text-xs font-medium text-slate-500 uppercase tracking-wider ml-1">
        {{ name }}
      </div>

      <!-- 消息气泡 -->
      <div class="bg-primary/10 text-slate-800 px-3 py-2 rounded-xl rounded-tl-none shadow-sm">
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