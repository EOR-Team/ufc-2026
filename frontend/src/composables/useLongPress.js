import { ref } from 'vue'

/**
 * 长按交互 Composable
 *
 * @param {number} duration - 触发长按所需的持续时间（毫秒），默认 350ms
 * @returns {{ isActive: Ref<boolean>, start: Function, end: Function, preventClick: Function }}
 */
export function useLongPress(duration = 350) {
  const isActive = ref(false)
  let timer = null

  /** 按下时启动计时器 */
  const start = () => {
    timer = setTimeout(() => {
      isActive.value = true
    }, duration)
  }

  /** 松开或离开时清除计时器并重置状态 */
  const end = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
    isActive.value = false
  }

  /** 阻止短按触发 click 事件干扰长按逻辑 */
  const preventClick = (e) => e.preventDefault()

  return { isActive, start, end, preventClick }
}
