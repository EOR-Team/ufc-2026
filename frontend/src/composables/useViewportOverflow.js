import { ref, onMounted, onUpdated, onUnmounted, nextTick } from 'vue'

/**
 * 视口溢出检测 Composable
 *
 * 检测 #main-display-block 自身高度是否超过 #app 视口高度。
 * 若超过，则为 #app 添加 .content-exceeds-viewport 类，
 * 触发 style.css 中的顶部对齐规则（align-items: flex-start）。
 *
 * 注意：不应比较内部滚动内容的 scrollHeight，那只影响列表内部滚动，
 * 不代表外层容器溢出视口。
 *
 * @returns {{ contentExceedsViewport: Ref<boolean> }}
 */
export function useViewportOverflow() {
  const contentExceedsViewport = ref(false)

  const check = () => {
    nextTick(() => {
      const container = document.getElementById('main-display-block')
      const appEl = document.getElementById('app')

      if (container && appEl) {
        // 正确逻辑：判断 #main-display-block 自身是否超出 #app 视口高度，
        // 而非判断内部滚动内容高度（那只会触发列表内部滚动条，不影响外层布局）。
        const exceeds = container.offsetHeight > appEl.clientHeight
        contentExceedsViewport.value = exceeds
        // 将类添加到 #app，与 style.css 的 #app.content-exceeds-viewport 规则匹配
        appEl.classList.toggle('content-exceeds-viewport', exceeds)
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
