<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useVoiceRecorder } from '@/composables/useVoiceRecorder'
import { useViewportOverflow } from '@/composables/useViewportOverflow'
import { useApiStore } from '@/stores/api.js'
import { transformTextForSpeech } from '@/utils/textToSpeech.js'

const router = useRouter()
const apiStore = useApiStore()

// 语音长按状态
const { isActive: isListening, start: longPressStart, end: longPressEnd } = useLongPress(500)

// 语音录制
const voiceRecorder = useVoiceRecorder()
const isProcessingVoice = ref(false)

// 内容溢出检测（自动挂载监听）
useViewportOverflow()

// 有对话内容时才显示底部 spacer（防止初始状态可滚动）
const showSpacer = computed(() => medicalMessages.value.length > 1)

// 滚动容器引用
const scrollContainer = ref(null)

// 消息列表（只保留初始欢迎语）
const medicalMessages = ref([
  { name: 'assistant', message: '你好！我是智能医患助手，可以帮你解答医疗问题、提供健康建议。' },
])

// 监听长按状态：长按成功时开始录音
watch(isListening, async (newVal, oldVal) => {
  if (newVal === true && oldVal === false) {
    if (voiceRecorder.isRecording.value) return
    await voiceRecorder.startRecording()
  }
})

// 新消息时自动滚动到底部
watch(
  () => medicalMessages.value.length,
  async () => {
    await nextTick()
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  }
)

// 处理按下 FAB
const handlePressStart = () => {
  longPressStart()
}

// 处理松开 FAB
const handlePressEnd = async () => {
  longPressEnd()

  if (isProcessingVoice.value) return
  if (!voiceRecorder.isRecording.value) return

  isProcessingVoice.value = true

  try {
    const audioBlob = await voiceRecorder.stopRecording()

    if (!audioBlob) {
      isProcessingVoice.value = false
      return
    }

    // 用户骨架屏消息
    medicalMessages.value.push({
      name: 'user',
      message: '...',
      isSkeleton: true,
      isProcessing: true,
    })

    // STT
    const sttResponse = await apiStore.speechToText(audioBlob)

    if (!sttResponse.success) {
      medicalMessages.value[medicalMessages.value.length - 1] = {
        name: 'user',
        message: '语音识别失败，请重试',
        isError: true,
      }
      isProcessingVoice.value = false
      return
    }

    const recognizedText = (sttResponse.data?.text || '').trim()

    if (!recognizedText) {
      medicalMessages.value[medicalMessages.value.length - 1] = {
        name: 'user',
        message: '未识别到有效语音，请重试',
        isError: true,
      }
      isProcessingVoice.value = false
      return
    }

    // 更新用户消息为识别结果
    medicalMessages.value[medicalMessages.value.length - 1] = {
      name: 'user',
      message: recognizedText,
    }

    // 助手骨架屏消息
    medicalMessages.value.push({
      name: 'assistant',
      message: '...',
      isSkeleton: true,
      isProcessing: true,
    })

    // 调用 medical API（只发最新一条，diagnosis 不传）
    const medicalResponse = await apiStore.getMedicalSuggestion(recognizedText)

    if (!medicalResponse.success) {
      medicalMessages.value[medicalMessages.value.length - 1] = {
        name: 'assistant',
        message: '获取医疗建议失败，请重试',
        isError: true,
      }
      isProcessingVoice.value = false
      return
    }

    const responseText = medicalResponse.data?.response || '抱歉，未能生成建议。'

    // 更新助手消息为真实回复
    medicalMessages.value[medicalMessages.value.length - 1] = {
      name: 'assistant',
      message: responseText,
    }

    // TTS 播放
    const speechText = transformTextForSpeech(responseText)
    if (speechText.trim()) {
      const ttsBlob = await apiStore.tts(speechText)
      if (ttsBlob) {
        const audioUrl = URL.createObjectURL(ttsBlob)
        const audio = new Audio(audioUrl)
        audio.onended = () => URL.revokeObjectURL(audioUrl)
        audio.play().catch(err => console.warn('[TTS] Playback failed:', err))
      }
    }

  } catch (err) {
    console.error('[MedicalView] Error:', err)
    const last = medicalMessages.value[medicalMessages.value.length - 1]
    if (last?.isProcessing) {
      medicalMessages.value[medicalMessages.value.length - 1] = {
        name: last.name,
        message: '处理出错，请重试',
        isError: true,
      }
    }
  } finally {
    isProcessingVoice.value = false
  }
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
        <div ref="scrollContainer" class="overflow-y-auto no-scrollbar" style="height: 471px;">
          <ConversationList :messages="medicalMessages" />
          <div v-show="showSpacer" style="height: 300px;" />
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