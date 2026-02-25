<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useViewportOverflow } from '@/composables/useViewportOverflow'
import { useWorkflowStore } from '@/stores/workflow.js'
import { useApiStore } from '@/stores/api.js'

const router = useRouter()

// 语音长按状态
const { isActive: isListening, start, end } = useLongPress(250)

// 内容溢出检测（自动挂载监听）
useViewportOverflow()

// 工作流状态管理
const workflowStore = useWorkflowStore()
const apiStore = useApiStore()

// 使用工作流存储的消息
const navigationMessages = computed(() => workflowStore.messages)


// 初始化工作流
onMounted(() => {
  // 如果工作流处于空闲状态且没有消息，自动开始
  if (workflowStore.isIdle && workflowStore.messages.length === 0) {
    workflowStore.startWorkflow()
  }
})

// 处理语音输入
const handleVoiceInput = async (text) => {
  if (!text || !text.trim()) return

  const input = text.trim()

  // 检查是否为重启命令
  if (input === '重新开始' || input === 'restart') {
    workflowStore.resetWorkflow()
    workflowStore.startWorkflow()
    return
  }

  // 处理用户输入
  await workflowStore.processUserInput(input)
}
</script>

<template>
  <FixedAspectContainer
    bg-color-class="bg-white"
    extra-class="font-display"
    :overflow-hidden="false"
  >
    <!-- 顶部应用栏 -->
    <AppTopBar
      @settings-click="router.push({ name: 'settings' })"
    />


    <!-- 主内容区（相对定位，供 VoiceOverlay 绝对定位参考） -->
    <div class="flex-1 flex flex-col relative min-h-0">
      <!-- 滚动容器：独立处理滚动 -->
      <div class="relative flex-1 min-h-0">
        <!-- 内容容器 -->
        <div class="overflow-y-auto no-scrollbar" style="height: 400px;">
          <ConversationList :messages="navigationMessages" />
        </div>
      </div>


      <VoiceOverlay :visible="isListening" />
    </div>

    <!-- 底部导航栏 + FAB -->
    <AppBottomNav
      :is-listening="isListening"
      @press-start="start"
      @press-end="end"
    />

    <div class="h-1 bg-white" />
  </FixedAspectContainer>
</template>