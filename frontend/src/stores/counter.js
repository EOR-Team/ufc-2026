import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 使用组合式 API 风格定义 store（与 Vue3 组合式 API 保持一致）
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  function decrement() {
    count.value--
  }

  function reset() {
    count.value = 0
  }

  return { count, doubleCount, increment, decrement, reset }
})
