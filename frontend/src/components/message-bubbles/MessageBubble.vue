<script setup>
import { computed } from 'vue'
import BasicMessageBubble from './BasicMessageBubble.vue'
import SkeletonMessageBubble from './SkeletonMessageBubble.vue'

const props = defineProps({
  /**
   * 消息内容
   */
  message: {
    type: String,
    required: true
  },
  /**
   * 发送者类型
   * - 'assistant': 助手消息
   * - 'user': 用户消息
   */
  name: {
    type: String,
    required: true,
    validator: (value) => ['assistant', 'user'].includes(value)
  },
  /**
   * 自定义发送者名称（可选）
   */
  customName: {
    type: String,
    default: null
  },
  /**
   * 自定义图标名称（可选）
   */
  customIcon: {
    type: String,
    default: null
  },
  /**
   * 是否为骨架屏/加载状态消息
   */
  isSkeleton: {
    type: Boolean,
    default: false
  },
  /**
   * 是否正在等待 TTS 就绪（文字已写入但视觉上仍显示骨架屏）
   */
  isAwaitingTTS: {
    type: Boolean,
    default: false
  },
  /**
   * 是否为流式显示消息
   */
  isStreaming: {
    type: Boolean,
    default: false
  },
  /**
   * 流式显示进度（0-100）
   */
  streamingProgress: {
    type: Number,
    default: 0
  }
})

// 根据 name 类型决定默认的图标和名称
const bubbleConfig = computed(() => {
  const configs = {
    assistant: {
      name: props.customName || '助手',
      icon: props.customIcon || 'smart_toy',
      isAssistant: true
    },
    user: {
      name: props.customName || '用户',
      icon: props.customIcon || 'person',
      isAssistant: false
    }
  }
  
  return configs[props.name] || configs.assistant
})

// 计算属性
const { name: bubbleName, icon: bubbleIcon, isAssistant } = bubbleConfig.value

// 决定渲染哪个组件
const shouldRenderSkeleton = computed(() => {
  return props.isSkeleton || props.isAwaitingTTS
})
</script>

<template>
  <div class="message-container">
    <SkeletonMessageBubble
      v-if="shouldRenderSkeleton"
      :name="bubbleName"
      :icon="bubbleIcon"
      :is-assistant="isAssistant"
      animation-type="blinking"
    />
    <BasicMessageBubble
      v-else
      :message="message"
      :name="bubbleName"
      :icon="bubbleIcon"
      :is-assistant="isAssistant"
    />

    <!-- 挂载点 -->
    <div v-if="$slots.hook" class="message-hook-container">
      <slot name="hook"></slot>
    </div>
  </div>
</template>

<style scoped>
.message-container {
  display: flex;
  flex-direction: column;
}

.message-hook-container {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}
</style>