<script setup>
import BasicMessageBubble from './BasicMessageBubble.vue'

const props = defineProps({
  /**
   * 消息内容
   */
  message: {
    type: String,
    required: true
  },
  /**
   * 助手名称，默认为"助手"
   */
  name: {
    type: String,
    default: '助手'
  },
  /**
   * 图标名称，默认为"smart_toy"
   */
  icon: {
    type: String,
    default: 'smart_toy'
  }
})
</script>

<template>
  <BasicMessageBubble
    :message="message"
    :name="name"
    :icon="icon"
  />
</template>