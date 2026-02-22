<script setup>
import ListeningIndicator from '@/components/ListeningIndicator.vue'

/**
 * VoiceOverlay — 语音交互浮层
 *
 * 包含两层：
 *   1. blur-layer：毛玻璃蒙版，模糊背景内容
 *   2. ListeningIndicator：音频波形 + "正在倾听..."文字
 * 两层均通过 `visible` prop 控制，Fade In / Out 过渡效果同步触发。
 *
 * Props:
 *   visible (boolean) — 是否显示浮层
 */
defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <!-- Blur Layer：毛玻璃蒙版，z-20 -->
  <Transition name="blur-fade">
    <div
      v-if="visible"
      class="blur-layer absolute inset-0 pointer-events-none z-20"
    />
  </Transition>

  <!-- Listening Indicator：波形指示器，z-30 浮于蒙版之上 -->
  <Transition name="fade">
    <div
      v-if="visible"
      class="absolute inset-0 pointer-events-none flex items-center justify-center bg-transparent z-30"
    >
      <ListeningIndicator />
    </div>
  </Transition>
</template>

<style scoped>
/* 毛玻璃蒙版样式 */
.blur-layer {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

/* ListeningIndicator fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* blur-layer fade */
.blur-fade-enter-active,
.blur-fade-leave-active {
  transition: opacity 0.25s ease;
}
.blur-fade-enter-from,
.blur-fade-leave-to {
  opacity: 0;
}
</style>
