<script setup>
/**
 * SettingsItem — 设置行基底组件
 *
 * 提供统一的"图标 + 标签 + 可选说明"行骨架。
 * 右侧控件通过 #right slot 注入，行下方扩展内容通过 #below slot 注入（如滑块）。
 *
 * Props:
 *   icon        — Material Symbols 图标名称
 *   label       — 主标签文字
 *   description — 副标签文字（可选）
 *   divider     — 是否在行底部显示分隔线
 *   rowClass    — 覆盖默认垂直内边距（默认 'py-3'）
 */
defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  description: { type: String, default: null },
  divider: { type: Boolean, default: false },
  rowClass: { type: String, default: 'py-3' },
})
</script>

<template>
  <div :class="['px-4', rowClass, divider ? 'border-b border-slate-100' : '']">
    <!-- 主行：左侧信息 + 右侧控件 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3 min-w-0">
        <span class="material-symbols-outlined text-slate-400 shrink-0">{{ icon }}</span>
        <div class="flex flex-col gap-0.5 min-w-0">
          <span class="text-base font-medium">{{ label }}</span>
          <span v-if="description" class="text-xs text-slate-500">{{ description }}</span>
        </div>
      </div>
      <slot name="right" />
    </div>
    <!-- 行下方扩展区（如滑块轨道） -->
    <div v-if="$slots.below" class="mt-2">
      <slot name="below" />
    </div>
  </div>
</template>
