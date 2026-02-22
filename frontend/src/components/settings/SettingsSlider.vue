<script setup>
/**
 * SettingsSlider — 数值滑动条设置行
 *
 * 基于 SettingsItem，右侧显示当前值，行下方渲染全宽滑轨，支持 v-model。
 *
 * Props:
 *   icon         — Material Symbols 图标名称
 *   label        — 主标签文字
 *   divider      — 是否显示行底分隔线
 *   modelValue   — 当前数值（v-model）
 *   min          — 最小值，默认 0
 *   max          — 最大值，默认 100
 *   displayValue — 自定义显示文字（不传则默认显示 "值%"）
 */
import { computed } from 'vue'
import SettingsItem from './SettingsItem.vue'

const props = defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  divider: { type: Boolean, default: false },
  modelValue: { type: Number, required: true },
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  displayValue: { type: String, default: null },
})

const emit = defineEmits(['update:modelValue'])

const pct = computed(() => ((props.modelValue - props.min) / (props.max - props.min)) * 100 + '%')
const display = computed(() => props.displayValue ?? `${props.modelValue}%`)
</script>

<template>
  <SettingsItem :icon="icon" :label="label" :divider="divider" row-class="pt-3 pb-4">
    <template #right>
      <span class="text-primary font-bold text-sm ml-3 shrink-0">{{ display }}</span>
    </template>
    <template #below>
      <input
        :value="modelValue"
        @input="emit('update:modelValue', Number($event.target.value))"
        type="range"
        :min="min"
        :max="max"
        class="slider-input"
        :style="{ '--pct': pct }"
      />
    </template>
  </SettingsItem>
</template>

<style scoped>
.slider-input {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 9999px;
  background: linear-gradient(
    to right,
    #4252b3 0%,
    #4252b3 var(--pct, 50%),
    #f1f5f9 var(--pct, 50%),
    #f1f5f9 100%
  );
  outline: none;
  cursor: pointer;
}
.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid #4252b3;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}
.slider-input::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid #4252b3;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}
</style>
