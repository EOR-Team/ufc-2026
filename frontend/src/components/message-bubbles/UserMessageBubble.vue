<script setup>
import BasicMessageBubble from './BasicMessageBubble.vue'

const props = defineProps({
  /**
   * 消息内容
   */
  message: {
    type: String,
    required: true
  },
  /**
   * 用户名称，默认为"用户"
   */
  name: {
    type: String,
    default: '用户'
  },
  /**
   * 图标名称，默认为"person"
   */
  icon: {
    type: String,
    default: 'person'
  }
})
</script>

<template>
  <div class="flex items-start gap-3 flex-row-reverse mt-2 mb-2 ml-3 mr-3">
    <!-- 用户图标 -->
    <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center shrink-0 ml-3">
      <span class="material-symbols-outlined text-slate-700">
        {{ icon }}
      </span>
    </div>

    <!-- 消息内容区域 -->
    <div class="flex flex-col gap-1" style="max-width: 80%">
      <!-- 名称标签 -->
      <div class="text-xs font-medium text-slate-500 uppercase tracking-wider text-right mr-1">
        {{ name }}
      </div>

      <!-- 消息气泡 -->
      <div class="bg-slate-200 text-slate-800 px-3 py-2 rounded-xl rounded-tr-none shadow-sm">
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