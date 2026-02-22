<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'

const router = useRouter()

// 常规设置
const voiceWakeup = ref(true)
const continuousConversation = ref(false)

// 声音设置
const volume = ref(75)
const speechRate = ref(50) // 50% = 1.0x
</script>

<template>
  <FixedAspectContainer 
    width="332"
    :height="774.66"
    bg-color-class="bg-white"
    extra-class="font-display text-slate-900 antialiased overflow-y-auto"
    :shadow="true"
  >

    <!-- Top Navigation Bar -->
    <header class="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/60">
      <div class="flex items-center justify-between px-3 h-12 max-w-2xl mx-auto">
        <button
          @click="router.back()"
          class="flex items-center justify-center size-10 rounded-full hover:bg-slate-200 transition-colors"
        >
          <span class="material-symbols-outlined text-slate-700">arrow_back</span>
        </button>
        <p class="text-lg font-bold tracking-tight text-slate-800 m-0">设置</p>
        <div class="size-10"></div>
      </div>
    </header>

    <main class="max-w-2xl mx-auto pb-3 pt-3">

      <!-- 常规设置 -->
      <div class="px-3 mb-3">
        <p class="px-2 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 m-0">常规设置</p>
        <div class="bg-white rounded-xl overflow-hidden shadow-sm border border-slate-100">

          <!-- 语音唤醒 -->
          <div class="flex items-center justify-between p-3 border-b border-slate-100">
            <div class="flex flex-col gap-0.5">
              <span class="text-base font-medium">语音唤醒</span>
              <span class="text-xs text-slate-500">通过 '嘿，助手' 唤醒设备</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="voiceWakeup" type="checkbox" class="sr-only peer" />
              <div class="toggle-track peer-checked:bg-primary"></div>
            </label>
          </div>

          <!-- 连续对话 -->
          <div class="flex items-center justify-between p-3">
            <div class="flex flex-col gap-0.5">
              <span class="text-base font-medium">连续对话</span>
              <span class="text-xs text-slate-500">无需重复唤醒即可进行多轮对话</span>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input v-model="continuousConversation" type="checkbox" class="sr-only peer" />
              <div class="toggle-track peer-checked:bg-primary"></div>
            </label>
          </div>

        </div>
      </div>

      <!-- 声音设置 -->
      <div class="px-3 mb-3">
        <p class="px-2 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 m-0">声音设置</p>
        <div class="bg-white rounded-xl overflow-hidden shadow-sm border border-slate-100 p-3 space-y-3">

          <!-- 音量 -->
          <div class="flex items-center gap-3 py-1">
            <div class="flex items-center gap-2 min-w-[72px]">
              <span class="material-symbols-outlined text-slate-400" style="font-size:20px">volume_up</span>
              <span class="text-sm font-medium">音量</span>
            </div>
            <div class="relative flex-1 h-6 flex items-center">
              <input
                v-model="volume"
                type="range" min="0" max="100"
                class="slider-input"
                :style="{ '--pct': volume + '%' }"
              />
            </div>
            <span class="text-primary font-bold text-sm min-w-[40px] text-right">{{ volume }}%</span>
          </div>

          <!-- 语速 -->
          <div class="flex items-center gap-3 py-1">
            <div class="flex items-center gap-2 min-w-[72px]">
              <span class="material-symbols-outlined text-slate-400" style="font-size:20px">speed</span>
              <span class="text-sm font-medium">语速</span>
            </div>
            <div class="relative flex-1 h-6 flex items-center">
              <input
                v-model="speechRate"
                type="range" min="0" max="100"
                class="slider-input"
                :style="{ '--pct': speechRate + '%' }"
              />
            </div>
            <span class="text-primary font-bold text-sm min-w-[40px] text-right">
              {{ speechRate <= 25 ? '0.75x' : speechRate <= 50 ? '1.0x' : speechRate <= 75 ? '1.25x' : '1.5x' }}
            </span>
          </div>

        </div>
      </div>

      <!-- 其他 -->
      <div class="px-3 mb-3">
        <p class="px-2 mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500 m-0">其他</p>
        <div class="bg-white rounded-xl overflow-hidden shadow-sm border border-slate-100">
          <button class="w-full flex items-center justify-between p-3 border-b border-slate-100 hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-slate-400">description</span>
              <span class="text-base font-medium">隐私权政策</span>
            </div>
            <span class="material-symbols-outlined text-slate-300">chevron_right</span>
          </button>
          <button class="w-full flex items-center justify-between p-3 hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-slate-400">info</span>
              <span class="text-base font-medium">关于我们</span>
            </div>
            <span class="material-symbols-outlined text-slate-300">chevron_right</span>
          </button>
        </div>
      </div>

    </main>
  </FixedAspectContainer>
</template>

<style scoped>
/* Toggle switch */
.toggle-track {
  position: relative;
  width: 44px;
  height: 24px;
  background-color: #e2e8f0;
  border-radius: 9999px;
  transition: background-color 0.2s;
}
.toggle-track::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 9999px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}
.peer:checked ~ .toggle-track {
  background-color: #4252b3;
}
.peer:checked ~ .toggle-track::after {
  transform: translateX(20px);
}

/* Range slider */
.slider-input {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 9999px;
  background: linear-gradient(
    to right,
    #4252b3 0%,
    #4252b3 var(--pct, 50%),
    #f1f5f9 var(--pct, 50%),
    #f1f5f9 100%
  );
  outline: none;
  cursor: pointer;
}
.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid #4252b3;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  cursor: pointer;
}
.slider-input::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid #4252b3;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  cursor: pointer;
}
</style>
