/**
 * 流式文本显示工具
 *
 * 提供文本流式显示功能，支持字符逐个显示或单词逐个显示动画。
 * 可以与 Vue 组件集成，实现打字机效果。
 */

/**
 * 流式显示配置选项
 * @typedef {Object} StreamingOptions
 * @property {'char' | 'word'} mode - 显示模式：字符逐个显示或单词逐个显示
 * @property {number} speed - 显示速度（字符/毫秒）
 * @property {number} delay - 开始前的延迟（毫秒）
 * @property {Function} onProgress - 进度回调 (progress: number, displayedText: string) => void
 * @property {Function} onComplete - 完成回调 () => void
 * @property {boolean} useRequestAnimationFrame - 是否使用 requestAnimationFrame 进行动画
 */

/**
 * 默认配置
 * @type {StreamingOptions}
 */
const DEFAULT_OPTIONS = {
  mode: 'char',
  speed: 50, // 每50毫秒一个字符
  delay: 0,
  onProgress: null,
  onComplete: null,
  useRequestAnimationFrame: true
}

/**
 * 流式文本显示控制器
 */
class StreamingDisplayController {
  /**
   * 创建控制器
   * @param {HTMLElement} element - 要显示文本的 DOM 元素
   * @param {string} text - 要显示的完整文本
   * @param {StreamingOptions} options - 配置选项
   */
  constructor(element, text, options = {}) {
    this.element = element
    this.fullText = text
    this.options = { ...DEFAULT_OPTIONS, ...options }

    this.currentIndex = 0
    this.isPlaying = false
    this.isComplete = false
    this.animationFrameId = null
    this.timeoutId = null
    this.startTime = 0

    // 初始化显示空文本
    this.updateDisplay('')
  }

  /**
   * 开始流式显示
   * @returns {Promise<void>}
   */
  async start() {
    if (this.isPlaying || this.isComplete) {
      return
    }

    this.isPlaying = true
    this.isComplete = false

    // 延迟开始
    if (this.options.delay > 0) {
      await new Promise(resolve => setTimeout(resolve, this.options.delay))
    }

    this.startTime = Date.now()

    if (this.options.useRequestAnimationFrame) {
      this.animateWithRAF()
    } else {
      this.animateWithTimeout()
    }
  }

  /**
   * 使用 requestAnimationFrame 进行动画
   */
  animateWithRAF() {
    const animate = () => {
      if (!this.isPlaying) {
        return
      }

      const elapsed = Date.now() - this.startTime
      const targetIndex = Math.floor(elapsed / this.options.speed)

      if (targetIndex >= this.getMaxIndex()) {
        this.complete()
        return
      }

      this.currentIndex = targetIndex
      this.updateDisplay(this.getDisplayedText())

      if (this.options.onProgress) {
        const progress = (this.currentIndex / this.getMaxIndex()) * 100
        this.options.onProgress(progress, this.getDisplayedText())
      }

      this.animationFrameId = requestAnimationFrame(animate)
    }

    this.animationFrameId = requestAnimationFrame(animate)
  }

  /**
   * 使用 setTimeout 进行动画
   */
  animateWithTimeout() {
    const animate = () => {
      if (!this.isPlaying) {
        return
      }

      this.currentIndex++
      this.updateDisplay(this.getDisplayedText())

      if (this.options.onProgress) {
        const progress = (this.currentIndex / this.getMaxIndex()) * 100
        this.options.onProgress(progress, this.getDisplayedText())
      }

      if (this.currentIndex >= this.getMaxIndex()) {
        this.complete()
      } else {
        this.timeoutId = setTimeout(animate, this.options.speed)
      }
    }

    this.timeoutId = setTimeout(animate, this.options.speed)
  }

  /**
   * 获取最大索引（根据模式不同）
   * @returns {number}
   */
  getMaxIndex() {
    if (this.options.mode === 'char') {
      return this.fullText.length
    } else {
      // 单词模式：按空格分割单词
      const words = this.fullText.split(/\s+/)
      return words.length
    }
  }

  /**
   * 获取当前显示的文本
   * @returns {string}
   */
  getDisplayedText() {
    if (this.options.mode === 'char') {
      return this.fullText.substring(0, this.currentIndex)
    } else {
      // 单词模式：显示指定数量的单词
      const words = this.fullText.split(/\s+/)
      const displayedWords = words.slice(0, this.currentIndex)
      return displayedWords.join(' ')
    }
  }

  /**
   * 更新 DOM 元素显示
   * @param {string} text
   */
  updateDisplay(text) {
    if (this.element) {
      this.element.textContent = text

      // 对于输入框等元素，可能需要设置 value
      if (this.element.value !== undefined) {
        this.element.value = text
      }
    }
  }

  /**
   * 完成显示
   */
  complete() {
    this.isPlaying = false
    this.isComplete = true
    this.currentIndex = this.getMaxIndex()
    this.updateDisplay(this.fullText)

    // 清理动画
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }

    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }

    if (this.options.onComplete) {
      this.options.onComplete()
    }
  }

  /**
   * 暂停显示
   */
  pause() {
    this.isPlaying = false

    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }

    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
      this.timeoutId = null
    }
  }

  /**
   * 恢复显示
   */
  resume() {
    if (this.isComplete) {
      return
    }

    this.isPlaying = true
    this.startTime = Date.now() - (this.currentIndex * this.options.speed)

    if (this.options.useRequestAnimationFrame) {
      this.animateWithRAF()
    } else {
      this.animateWithTimeout()
    }
  }

  /**
   * 跳转到指定进度
   * @param {number} progress - 进度百分比 (0-100)
   */
  jumpTo(progress) {
    const clampedProgress = Math.max(0, Math.min(100, progress))
    const targetIndex = Math.floor((clampedProgress / 100) * this.getMaxIndex())

    this.currentIndex = targetIndex
    this.updateDisplay(this.getDisplayedText())

    if (this.options.onProgress) {
      this.options.onProgress(clampedProgress, this.getDisplayedText())
    }

    // 如果正在进行动画，重新计算开始时间
    if (this.isPlaying) {
      this.startTime = Date.now() - (this.currentIndex * this.options.speed)
    }
  }

  /**
   * 跳过动画，立即显示完整文本
   */
  skip() {
    this.pause()
    this.complete()
  }

  /**
   * 销毁控制器，清理资源
   */
  destroy() {
    this.pause()
    this.element = null
    this.options = {}
  }
}

/**
 * 在元素上流式显示文本
 * @param {HTMLElement} element - DOM 元素
 * @param {string} text - 要显示的文本
 * @param {StreamingOptions} options - 配置选项
 * @returns {StreamingDisplayController} 控制器实例
 */
export function displayTextStreamingly(element, text, options = {}) {
  const controller = new StreamingDisplayController(element, text, options)
  controller.start()
  return controller
}

/**
 * 创建流式文本显示函数（与 Vue 响应式数据集成）
 * @param {Ref<string>} textRef - Vue 响应式文本引用
 * @param {StreamingOptions} options - 配置选项
 * @returns {Function} 开始显示的函数
 */
export function createStreamingDisplay(textRef, options = {}) {
  return (element) => {
    const controller = new StreamingDisplayController(element, textRef.value, options)

    // 监听文本变化（如果文本是响应式的）
    const unwatch = () => {}

    controller.start()
    return {
      controller,
      unwatch
    }
  }
}

/**
 * 计算流式显示进度
 * @param {string} fullText - 完整文本
 * @param {string} displayedText - 已显示文本
 * @param {'char' | 'word'} mode - 显示模式
 * @returns {number} 进度百分比 (0-100)
 */
export function calculateStreamingProgress(fullText, displayedText, mode = 'char') {
  if (!fullText || !displayedText) {
    return 0
  }

  if (mode === 'char') {
    const progress = (displayedText.length / fullText.length) * 100
    return Math.min(100, Math.max(0, progress))
  } else {
    const fullWords = fullText.split(/\s+/).length
    const displayedWords = displayedText.split(/\s+/).length
    const progress = (displayedWords / fullWords) * 100
    return Math.min(100, Math.max(0, progress))
  }
}

/**
 * 流式显示文本到多个元素的辅助函数
 * @param {Array<{element: HTMLElement, text: string}>} items - 要显示的元素和文本数组
 * @param {StreamingOptions} options - 配置选项
 * @returns {StreamingDisplayController[]} 控制器数组
 */
export function displayMultipleTextsStreamingly(items, options = {}) {
  return items.map(item => {
    const controller = new StreamingDisplayController(item.element, item.text, options)
    controller.start()
    return controller
  })
}