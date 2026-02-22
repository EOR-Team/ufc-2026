<script setup>
import { computed } from 'vue'

/**
 * FixedAspectContainer — 固定尺寸页面容器
 *
 * 默认尺寸：300 × 600px
 * 所有页面级组件应以此为根容器，确保视觉一致性。
 */
const props = defineProps({
  /** 容器宽度（px），默认 332 */
  width: {
    type: [Number, String],
    default: 300,
  },
  /** 容器高度（px），默认 720 */
  height: {
    type: [Number, String],
    default: 600,
  },
  /** 背景颜色 Tailwind 类 */
  bgColorClass: {
    type: String,
    default: 'bg-white',
  },
  /** 是否显示投影 */
  shadow: {
    type: Boolean,
    default: true,
  },
  /** 是否裁切溢出内容 */
  overflowHidden: {
    type: Boolean,
    default: true,
  },
  /** 附加 Tailwind 类 */
  extraClass: {
    type: String,
    default: '',
  },
})

const toPx = (val) =>
  typeof val === 'number' ? `${val}px` : val.includes('px') ? val : `${val}px`

const containerStyle = computed(() => ({
  width: toPx(props.width),
  height: toPx(props.height),
}))

const containerClass = computed(() =>
  [
    'fixed-aspect-container',
    'relative',
    'flex',
    'flex-col',
    props.overflowHidden ? 'overflow-hidden' : '',
    props.bgColorClass,
    props.shadow ? 'shadow-2xl' : '',
    props.extraClass,
  ]
    .filter(Boolean)
    .join(' ')
)
</script>

<template>
  <div id="main-display-block" :class="containerClass" :style="containerStyle">
    <slot></slot>
  </div>
</template>

<style scoped>
/* 组件特定样式（如果有的话） */
</style>