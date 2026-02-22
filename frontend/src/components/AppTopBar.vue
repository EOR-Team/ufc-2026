<script setup>
/**
 * AppTopBar — 顶部应用栏
 *
 * Props:
 *   title (string) — 标题文本，默认"语音助手"
 *
 * Emits:
 *   settings-click — 点击设置按钮时触发
 */
defineProps({
  title: {
    type: String,
    default: '语音助手',
  },
})

const emit = defineEmits(['settings-click'])
</script>

<template>
  <header class="flex items-center bg-white px-3 py-3 justify-between border-b sticky top-0 z-40 border-primary/20">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white">
        <span class="material-symbols-outlined" style="font-size:18px">graphic_eq</span>
      </div>
      <p class="text-slate-900 text-xl font-semibold tracking-tight m-0">{{ title }}</p>
    </div>
    <button
      @click="emit('settings-click')"
      class="flex items-center justify-center rounded-full w-10 h-10 hover:bg-primary/10 transition-colors text-slate-600"
    >
      <span class="material-symbols-outlined">settings</span>
    </button>
  </header>
</template>
