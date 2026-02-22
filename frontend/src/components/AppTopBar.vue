<script setup>
/**
 * AppTopBar — 顶部应用栏
 *
 * 标题跟随 useChatModeStore.modeLabel 自动变化。
 *
 * Emits:
 *   settings-click — 点击设置按钮时触发
 */
import { useChatModeStore } from '@/stores/useChatModeStore'

const chatMode = useChatModeStore()
const emit = defineEmits(['settings-click'])
</script>

<template>
  <header class="flex items-center bg-white px-3 py-3 justify-between border-b sticky top-0 z-40 border-primary/20">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white">
        <span class="material-symbols-outlined" style="font-size:18px">graphic_eq</span>
      </div>
      <p class="text-slate-900 text-xl font-semibold tracking-tight m-0">{{ chatMode.modeLabel }}</p>
    </div>
    <button
      @click="emit('settings-click')"
      class="flex items-center justify-center rounded-full w-10 h-10 hover:bg-primary/10 transition-colors text-slate-600"
    >
      <span class="material-symbols-outlined">settings</span>
    </button>
  </header>
</template>
