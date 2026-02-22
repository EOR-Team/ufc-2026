import { ref, onMounted, onUpdated, onUnmounted, nextTick } from 'vue'

/**
 * 视口溢出检测 Composable
 *
 * 监测 #main-display-block 内 [data-conversation-list] 元素的内容高度，
 * 当内容超出容器时，为容器添加 .content-exceeds-viewport 类，
 * 触发 style.css 中的顶部对齐规则。
 *
 * @returns {{ contentExceedsViewport: Ref<boolean> }}
 */
export function useViewportOverflow() {
  const contentExceedsViewport = ref(false)

  const check = () => {
    nextTick(() => {
      const container = document.getElementById('main-display-block')
      const content = container?.querySelector('[data-conversation-list]')

      if (container && content) {
        const exceeds = content.scrollHeight > container.clientHeight
        contentExceedsViewport.value = exceeds
        container.classList.toggle('content-exceeds-viewport', exceeds)
      }
    })
  }

  onMounted(() => {
    check()
    window.addEventListener('resize', check)
  })

  onUpdated(() => check())

  onUnmounted(() => {
    window.removeEventListener('resize', check)
  })

  return { contentExceedsViewport }
}
