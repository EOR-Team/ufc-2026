<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useVoiceRecorder } from '@/composables/useVoiceRecorder'
import { useViewportOverflow } from '@/composables/useViewportOverflow'
import { useWorkflowStore } from '@/stores/workflow.js'
import { useApiStore } from '@/stores/api.js'

const router = useRouter()

// 语音长按状态
const { isActive: isListening, start: longPressStart, end: longPressEnd } = useLongPress(250)

// 语音录制
const voiceRecorder = useVoiceRecorder()
const isProcessingVoice = ref(false)
const currentSkeletonMessageId = ref(null)

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

// 处理按下 FAB（开始录音）
const handlePressStart = async () => {
  console.log('[NavigationView] FAB 按下，开始语音录制')

  // 开始长按计时器（显示 VoiceOverlay）
  longPressStart()

  // 开始语音录制
  const started = await voiceRecorder.startRecording()
  if (!started) {
    console.error('[NavigationView] 语音录制启动失败')
    // 如果录制失败，结束长按状态
    longPressEnd()
  }
}

// 处理松开 FAB（结束录音并发送到 STT）
const handlePressEnd = async () => {
  console.log('[NavigationView] FAB 松开，结束语音录制')

  // 结束长按计时器（隐藏 VoiceOverlay）
  longPressEnd()

  // 如果正在处理中，忽略
  if (isProcessingVoice.value) {
    console.warn('[NavigationView] 语音处理中，忽略新的松开事件')
    return
  }

  // 防止重复处理：设置处理标志
  isProcessingVoice.value = true

  // 额外的检查：确保有正在进行的录音
  if (!voiceRecorder.isRecording.value) {
    console.warn('[NavigationView] 没有正在进行的录音，忽略松开事件')
    isProcessingVoice.value = false
    return
  }

  try {
    // 停止录音并获取音频 Blob
    const audioBlob = await voiceRecorder.stopRecording()

    if (!audioBlob) {
      console.error('[NavigationView] 未获取到音频数据')
      isProcessingVoice.value = false
      return
    }

    console.log(`[NavigationView] 获取到音频数据，大小: ${audioBlob.size} 字节，类型: ${audioBlob.type}`)

    // 添加骨架屏消息到对话
    console.log('[NavigationView] 添加骨架屏消息')
    const skeletonMessage = workflowStore.addUserMessage('...', {
      isSkeleton: true,
      isStreaming: false,
      isProcessing: true
    })

    // 保存骨架屏消息的索引（最后一条消息）
    const skeletonMessageIndex = workflowStore.messages.length - 1
    console.log(`[NavigationView] 骨架屏消息索引: ${skeletonMessageIndex}`)

    // 发送音频到 STT API
    console.log('[NavigationView] 发送音频到 STT API...')
    const sttResponse = await apiStore.speechToText(audioBlob)

    if (!sttResponse.success) {
      console.error('[NavigationView] STT API 调用失败:', sttResponse.error)

      // 更新骨架屏消息为错误状态
      workflowStore.updateLastMessage({
        message: '语音识别失败，请重试',
        isSkeleton: false,
        isStreaming: false,
        isProcessing: false,
        isError: true
      })

      isProcessingVoice.value = false
      return
    }

    // 获取识别到的文本
    const recognizedText = sttResponse.data?.text || ''
    console.log('[NavigationView] 语音识别结果:', recognizedText)

    if (!recognizedText.trim()) {
      console.warn('[NavigationView] 识别结果为空')

      // 更新骨架屏消息为空结果提示
      workflowStore.updateLastMessage({
        message: '未识别到有效语音，请重试',
        isSkeleton: false,
        isStreaming: false,
        isProcessing: false,
        isError: true
      })

      isProcessingVoice.value = false
      return
    }

    // 更新骨架屏消息为流式文本消息
    console.log('[NavigationView] 更新消息为流式文本')
    workflowStore.updateLastMessage({
      message: recognizedText,
      isSkeleton: false,
      isStreaming: true, // 标记为流式文本，可以用于前端显示效果
      isProcessing: false,
      isError: false,
      streamingProgress: 100 // 初始进度，实际可以设置为0然后动画显示
    })

    // 调用现有的 handleVoiceInput 处理识别到的文本
    await handleVoiceInput(recognizedText)

  } catch (error) {
    console.error('[NavigationView] 语音处理过程中发生错误:', error)

    // 更新最后一条消息为错误状态
    if (workflowStore.messages.length > 0) {
      workflowStore.updateLastMessage({
        message: '语音处理错误，请重试',
        isSkeleton: false,
        isStreaming: false,
        isProcessing: false,
        isError: true
      })
    }
  } finally {
    isProcessingVoice.value = false
  }
}

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
      @press-start="handlePressStart"
      @press-end="handlePressEnd"
    />

    <div class="h-1 bg-white" />
  </FixedAspectContainer>
</template>