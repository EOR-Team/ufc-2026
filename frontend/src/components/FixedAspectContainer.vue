<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 宽度（像素）
  width: {
    type: [Number, String],
    default: 332
  },
  // 高度（像素），如果未提供则根据宽高比计算
  height: {
    type: [Number, String],
    default: null
  },
  // 宽高比，格式为 "宽度:高度"，例如 "9:21"
  aspectRatio: {
    type: String,
    default: '9:21'
  },
  // 最大宽度类
  maxWidthClass: {
    type: String,
    default: 'max-w-md'
  },
  // 背景颜色类
  bgColorClass: {
    type: String,
    default: 'bg-white'
  },
  // 是否显示阴影
  shadow: {
    type: Boolean,
    default: true
  },
  // 是否允许内容溢出
  overflowHidden: {
    type: Boolean,
    default: true
  },
  // 额外的CSS类
  extraClass: {
    type: String,
    default: ''
  }
})

// 计算最终的高度
const containerHeight = computed(() => {
  // 如果明确提供了高度，使用该高度
  if (props.height !== null) {
    return typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  
  // 否则根据宽高比计算高度
  const [widthRatio, heightRatio] = props.aspectRatio.split(':').map(Number)
  const widthValue = typeof props.width === 'number' ? props.width : parseInt(props.width)
  const calculatedHeight = (widthValue * heightRatio) / widthRatio
  return `${calculatedHeight}px`
})

// 计算最终的宽度
const containerWidth = computed(() => {
  if (typeof props.width === 'number') {
    return `${props.width}px`
  }
  // 如果是字符串，检查是否已经包含px单位
  if (typeof props.width === 'string' && props.width.includes('px')) {
    return props.width
  }
  // 否则添加px单位
  return `${props.width}px`
})

// 计算容器样式
const containerStyle = computed(() => {
  return {
    width: containerWidth.value,
    height: containerHeight.value
  }
})

// 计算容器类
const containerClass = computed(() => {
  const classes = [
    'fixed-aspect-container',
    'relative',
    'flex',
    'flex-col',
    props.overflowHidden ? 'overflow-hidden' : '',
    props.bgColorClass,
    props.shadow ? 'shadow-2xl' : '',
    props.extraClass
  ].filter(Boolean)
  
  return classes.join(' ')
})
</script>

<template>
  <div id="main-display-block" :class="containerClass" :style="containerStyle">
    <slot></slot>
  </div>
</template>

<style scoped>
/* 组件特定样式（如果有的话） */
</style>