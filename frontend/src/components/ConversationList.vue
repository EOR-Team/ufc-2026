<script setup>
import { computed } from 'vue'
import MessageBubble from '@/components/message-bubbles'
import MessageHook from '@/components/MessageHook.vue'

/**
 * ConversationList — 对话消息滚动列表
 *
 * Props:
 *   messages (Array) — 消息数组，每项包含 { name: 'assistant'|'user', message: string, ... }
 *                             支持所有 MessageBubble 支持的属性
 *   showMapButton (Boolean) — 是否显示地图按钮
 *
 * Events:
 *   view-map — 用户点击"查看地图"按钮时触发
 */
const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  // 新增：是否显示地图按钮
  showMapButton: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['view-map'])

// 判断最后一条助手消息是否包含路线
function containsRoute(messageObj) {
  if (!messageObj || !messageObj.message) return false

  const msg = messageObj.message.toLowerCase()
  // 检查消息中是否包含路线相关的关键词
  return msg.includes('路线') ||
         msg.includes('route') ||
         msg.includes('导航') ||
         msg.includes('前往') ||
         msg.includes('到达')
}

// 判断是否显示地图按钮
function shouldShowMapHook(msg, index) {
  return props.showMapButton &&
         index === props.messages.length - 1 &&
         msg.name === 'assistant' &&
         containsRoute(msg)
}

function handleViewMap() {
  emit('view-map')
}
</script>

<template>
  <div
    data-conversation-list
    class="h-full"
    style="padding: 12px;"
  >
    <div class="flex flex-col gap-3">
      <MessageBubble
        v-for="(msg, index) in messages"
        :key="index"
        v-bind="msg"
      >
        <!-- MessageHook 插槽 -->
        <template v-if="shouldShowMapHook(msg, index)" v-slot:hook>
          <MessageHook :on-click="handleViewMap" />
        </template>
      </MessageBubble>
    </div>
  </div>
</template>

<style scoped>
/* 滚动样式现在由外层容器处理 */
</style>
