<script setup>
/**
 * SettingsSection — 设置分组容器
 *
 * 封装"分组标题 + 白色圆角卡片"的公共外壳，内部行通过默认 slot 注入。
 *
 * Props:
 *   title — 分组标题文字（如"常规设置"）
 */
defineProps({
  title: { type: String, required: true },
})
</script>

<template>
  <div class="px-3 mb-4">
    <p class="px-2 mt-0 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
      {{ title }}
    </p>
    <div class="bg-white rounded-xl overflow-hidden shadow-sm border border-slate-100">
      <slot />
    </div>
  </div>
</template>
