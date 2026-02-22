<script setup>
/**
 * SettingsToggle — 开关设置行
 *
 * 基于 SettingsItem，右侧渲染 toggle switch，支持 v-model。
 *
 * Props:
 *   icon        — Material Symbols 图标名称
 *   label       — 主标签文字
 *   description — 副标签文字（可选）
 *   divider     — 是否显示行底分隔线
 *   modelValue  — 开关状态（v-model）
 */
import SettingsItem from './SettingsItem.vue'

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  description: { type: String, default: null },
  divider: { type: Boolean, default: false },
  modelValue: { type: Boolean, required: true },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <SettingsItem :icon="icon" :label="label" :description="description" :divider="divider">
    <template #right>
      <label class="relative inline-flex items-center cursor-pointer ml-3 shrink-0">
        <input
          :checked="modelValue"
          @change="emit('update:modelValue', $event.target.checked)"
          type="checkbox"
          class="sr-only peer"
        />
        <div class="toggle-track peer-checked:bg-primary"></div>
      </label>
    </template>
  </SettingsItem>
</template>

<style scoped>
.toggle-track {
  position: relative;
  width: 44px;
  height: 24px;
  background-color: #e2e8f0;
  border-radius: 9999px;
  transition: background-color 0.2s;
}
.toggle-track::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 9999px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
}
.peer:checked ~ .toggle-track {
  background-color: #4252b3;
}
.peer:checked ~ .toggle-track::after {
  transform: translateX(20px);
}
</style>
