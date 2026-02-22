<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatModeStore } from '@/stores/useChatModeStore'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import AppTopBar from '@/components/AppTopBar.vue'
import ConversationList from '@/components/ConversationList.vue'
import VoiceOverlay from '@/components/VoiceOverlay.vue'
import AppBottomNav from '@/components/AppBottomNav.vue'
import { useLongPress } from '@/composables/useLongPress'
import { useViewportOverflow } from '@/composables/useViewportOverflow'

const router = useRouter()
const chatMode = useChatModeStore()
const slideTransition = computed(() => `slide-${chatMode.direction}`)

// 进入页面时重置为默认模式（智能寻路）
onMounted(() => chatMode.reset())

// 语音长按状态
const { isActive: isListening, start, end } = useLongPress(250)

// 内容溢出检测（自动挂载监听）
useViewportOverflow()

// 消息列表（mock 数据，待后端对接）
const messages = ref([
  { name: 'assistant', message: '你好！今天有什么我可以帮你的吗？' },
  { name: 'user',      message: '我想去门诊部' },
  { name: 'assistant', message: '好的，我可以帮你导航到门诊部。请问你现在在哪里？' },
  { name: 'user',      message: '我在医院大厅' },
  { name: 'assistant', message: '明白了。从医院大厅到门诊部，你可以按照以下路线：\n\n1. 从医院大厅出发，向东走，经过咖啡厅。\n2. 继续直行，经过电梯和休息区。\n3. 在第一个路口右转，进入主走廊。\n4. 沿着主走廊一直走，直到看到门诊部的标志。\n\n如果你需要更详细的指引或者有任何问题，请随时告诉我！' },
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
      <!-- 动画容器：动态控制溢出，动画期间隐藏溢出，非动画期间允许溢出 -->
      <div 
        class="relative flex-1 min-h-0"
        :class="{ 'overflow-hidden': chatMode.isAnimating }"
      >
        <!-- Vue Transition：负责动画控制 -->
        <transition 
          :name="slideTransition"
          @before-enter="chatMode.startAnimation()"
          @after-enter="chatMode.endAnimation()"
          @before-leave="chatMode.startAnimation()"
          @after-leave="chatMode.endAnimation()"
        >
          <!-- 定位容器：确保填满空间（CSS中已设置position: absolute） -->
          <div :key="chatMode.mode">
            <!-- 滚动容器：独立处理滚动，使用固定高度而非100% -->
            <div class="overflow-y-auto no-scrollbar" style="height: 471px;">
              <ConversationList :messages="messages" />
            </div>
          </div>
        </transition>
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
