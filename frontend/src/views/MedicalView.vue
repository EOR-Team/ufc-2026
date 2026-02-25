<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useViewportOverflow } from '@/composables/useViewportOverflow'

const router = useRouter()

// 语音长按状态
const { isActive: isListening, start, end } = useLongPress(250)

// 内容溢出检测（自动挂载监听）
useViewportOverflow()

// 消息列表（独立的消息历史）
const medicalMessages = ref([
  { name: 'assistant', message: '你好！我是智能医患助手，可以帮你解答医疗问题、提供健康建议。' },
  { name: 'user',      message: '我有点头疼' },
  { name: 'assistant', message: '头疼可能有多种原因。请问您的头疼是持续性的还是间歇性的？有没有其他症状比如发烧、恶心？' },
  { name: 'user',      message: '持续性的，没有其他症状' },
  { name: 'assistant', message: '如果持续性头疼，建议您先测量血压。如果血压正常，可以考虑休息一下，补充水分。如果头疼持续超过24小时，建议您去神经内科就诊。\n\n请注意：我是AI助手，不能替代专业医疗诊断。如果症状严重，请及时就医。' },
])
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
        <div class="overflow-y-auto no-scrollbar" style="height: 471px;">
          <ConversationList :messages="medicalMessages" />
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