<script setup>
import MessageBubble from '@/components/message-bubbles'

/**
 * ConversationList — 对话消息滚动列表
 *
 * Props:
 *   messages (Array) — 消息数组，每项包含 { name: 'assistant'|'user', message: string }
 *
 * data-conversation-list 属性供 useViewportOverflow composable 定位内容高度。
 */
defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <div
    data-conversation-list
    class="flex-1 overflow-y-auto no-scrollbar min-h-0"
    style="padding: 12px;"
  >
    <div class="flex flex-col gap-3">
      <MessageBubble
        v-for="(msg, index) in messages"
        :key="index"
        :name="msg.name"
        :message="msg.message"
      />
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
