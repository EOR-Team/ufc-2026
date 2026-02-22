<script setup>
/**
 * SettingsLink — 可点击跳转设置行
 *
 * 基于 SettingsItem，整行渲染为 button，右侧显示 chevron_right。
 *
 * Props:
 *   icon    — Material Symbols 图标名称
 *   label   — 主标签文字
 *   divider — 是否显示行底分隔线
 *
 * Emits:
 *   click — 点击行时触发
 */
import SettingsItem from './SettingsItem.vue'

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  divider: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])
</script>

<template>
  <button
    :class="['w-full text-left transition-colors', divider ? 'border-b border-slate-100' : '']"
    @click="emit('click')"
  >
    <SettingsItem :icon="icon" :label="label">
      <template #right>
        <span class="material-symbols-outlined text-slate-300 ml-3 shrink-0">chevron_right</span>
      </template>
    </SettingsItem>
  </button>
</template>
