import { ref, computed } from 'vue'
import { defineStore, acceptHMRUpdate } from 'pinia'

/**
 * 聊天模式 Store
 *
 * mode: 'navigation' | 'medical'
 *   - 'navigation' → 智能寻路
 *   - 'medical'    → 智能医患
 */
export const useChatModeStore = defineStore('chatMode', () => {
  const mode = ref('navigation')
  // navigation → medical 为向左（新内容从右侧滑入）
  // medical → navigation 为向右（新内容从左侧滑入）
  const direction = ref('left')
  // 动画状态跟踪
  const isAnimating = ref(false)

  const modeLabel = computed(() => {
    return mode.value === 'navigation' ? '智能寻路' : '智能医患'
  })

  function setMode(newMode) {
    if (newMode === mode.value) return
    direction.value = newMode === 'medical' ? 'left' : 'right'
    mode.value = newMode
  }

  function reset() {
    direction.value = 'left'
    mode.value = 'navigation'
    isAnimating.value = false
  }

  // 动画控制方法
  function startAnimation() {
    isAnimating.value = true
  }

  function endAnimation() {
    isAnimating.value = false
  }

  return { mode, direction, modeLabel, isAnimating, setMode, reset, startAnimation, endAnimation }
})

// 让 Vite HMR 正确热替换 Pinia store，避免旧实例缓存导致新增状态字段无效
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useChatModeStore, import.meta.hot))
}
