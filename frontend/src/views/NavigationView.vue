<script setup>
import { onMounted, computed, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import MapOverlay from '@/components/map/MapOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useVoiceRecorder } from '@/composables/useVoiceRecorder'
import { useViewportOverflow } from '@/composables/useViewportOverflow'
import { useWorkflowStore } from '@/stores/workflow.js'
import { useApiStore } from '@/stores/api.js'
import { transformTextForSpeech } from '@/utils/textToSpeech.js'

const router = useRouter()

// 语音长按状态
const { isActive: isListening, start: longPressStart, end: longPressEnd } = useLongPress(500)

// 语音录制
const voiceRecorder = useVoiceRecorder()
const isProcessingVoice = ref(false)

// 内容溢出检测（自动挂载监听）
useViewportOverflow()

// 监听长按状态变化，在长按成功时开始录音
watch(isListening, async (newVal, oldVal) => {
  if (newVal === true && oldVal === false) {
    // 长按成功，开始录音
    // 避免重复启动录音
    if (voiceRecorder.isRecording.value) {
      return
    }
    const started = await voiceRecorder.startRecording()
    if (!started) {
      // 注意：录音失败但不结束长按状态，保持长按激活
      // 这样用户仍然可以看到 VoiceOverlay 并知道长按成功
    }
  }
})

// 工作流状态管理
const workflowStore = useWorkflowStore()
const apiStore = useApiStore()

// 使用工作流存储的消息
const navigationMessages = computed(() => workflowStore.messages)

// 滚动容器引用
const scrollContainer = ref(null)

// 新消息时自动滚动到底部
watch(
  () => navigationMessages.value.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  }
)

// TTS 播放
const playTTS = async (text) => {
  const speechText = transformTextForSpeech(text)
  if (!speechText.trim()) return
  const audioBlob = await apiStore.tts(speechText)
  if (!audioBlob) return
  const audioUrl = URL.createObjectURL(audioBlob)
  const audio = new Audio(audioUrl)
  audio.onended = () => URL.revokeObjectURL(audioUrl)
  audio.play().catch(err => console.warn('[TTS] Playback failed:', err))
}

const ttsProcessedTimestamps = new Set()
let ttsFirstAssistantSkipped = false

watch(
  () => workflowStore.messages,
  (messages) => {
    messages.forEach(msg => {
      if (msg.name !== 'assistant') return

      // Case 1: awaiting TTS — fetch audio first, then reveal message and play
      if (
        msg.isAwaitingTTS &&
        !ttsProcessedTimestamps.has(msg.timestamp)
      ) {
        ttsProcessedTimestamps.add(msg.timestamp)
        ;(async () => {
          const speechText = transformTextForSpeech(msg.message)
          const audioBlob = speechText.trim() ? await apiStore.tts(speechText) : null
          // Reveal message and unblock workflow
          workflowStore.signalTTSReady()
          // Play audio after reveal
          if (audioBlob) {
            const audioUrl = URL.createObjectURL(audioBlob)
            const audio = new Audio(audioUrl)
            audio.onended = () => URL.revokeObjectURL(audioUrl)
            audio.play().catch(err => console.warn('[TTS] Playback failed:', err))
          }
        })()
        return
      }

      // Case 2: normal revealed message
      if (
        !msg.isProcessing &&
        !msg.isSkeleton &&
        !msg.isError &&
        !msg.isAwaitingTTS &&
        !ttsProcessedTimestamps.has(msg.timestamp)
      ) {
        ttsProcessedTimestamps.add(msg.timestamp)
        if (!ttsFirstAssistantSkipped) {
          ttsFirstAssistantSkipped = true
          return
        }
        playTTS(msg.message)
      }
    })
  },
  { deep: true }
)


// 初始化工作流
onMounted(async () => {
  // 预加载地图数据
  const mapResponse = await apiStore.getMap()
  if (mapResponse.success) {
    workflowStore.mapData = mapResponse.data
  } else if (mapResponse.nodes) {
    // /api/map/ 直接返回地图数据，无 success 包装
    workflowStore.mapData = mapResponse
  }

  // 如果工作流处于空闲状态且没有消息，自动开始
  if (workflowStore.isIdle && workflowStore.messages.length === 0) {
    workflowStore.startWorkflow()
  }
})

// 处理按下 FAB（启动长按计时器）
const handlePressStart = async () => {
  // 开始长按计时器（显示 VoiceOverlay）
  longPressStart()
}

// 处理松开 FAB（结束录音并发送到 STT）
const handlePressEnd = async () => {
  // 结束长按计时器（隐藏 VoiceOverlay）
  longPressEnd()

  // 如果正在处理中，忽略
  if (isProcessingVoice.value) {
    return
  }

  // 防止重复处理：设置处理标志
  isProcessingVoice.value = true

  // 额外的检查：确保有正在进行的录音
  if (!voiceRecorder.isRecording.value) {
    isProcessingVoice.value = false
    return
  }

  try {
    // 停止录音并获取音频 Blob
    const audioBlob = await voiceRecorder.stopRecording()

    if (!audioBlob) {
      isProcessingVoice.value = false
      return
    }


    // 添加骨架屏消息到对话
    const skeletonMessage = workflowStore.addUserMessage('...', {
      isSkeleton: true,
      isStreaming: false,
      isProcessing: true
    })

    // 骨架屏消息是最后一条消息

    // 发送音频到 STT API
    const sttResponse = await apiStore.speechToText(audioBlob)

    if (!sttResponse.success) {

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

    if (!recognizedText.trim()) {

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

// 计算是否显示地图按钮
const showMapButton = computed(() => {
  return workflowStore.isCompleted && workflowStore.hasHighlightedMap
})

// 处理查看地图按钮点击
const handleViewMap = () => {
  workflowStore.showMap()
}

// 处理地图关闭
const handleMapClose = () => {
  workflowStore.hideMap()
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
        <div ref="scrollContainer" class="overflow-y-auto no-scrollbar" style="height: 400px;">
          <ConversationList
            :messages="navigationMessages"
            :show-map-button="showMapButton"
            @view-map="handleViewMap"
          />
        </div>
      </div>


      <VoiceOverlay :visible="isListening" />

      <!-- 地图 overlay -->
      <MapOverlay
        :visible="workflowStore.showMapOverlay"
        :highlighted-map="workflowStore.highlightedMap"
        @close="handleMapClose"
      />
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