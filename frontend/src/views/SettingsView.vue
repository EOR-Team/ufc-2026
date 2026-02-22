<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import SettingsToggle from '@/components/settings/SettingsToggle.vue'
import SettingsSlider from '@/components/settings/SettingsSlider.vue'
import SettingsLink from '@/components/settings/SettingsLink.vue'
import SettingsSection from '@/components/settings/SettingsSection.vue'

const router = useRouter()

// 常规设置
const voiceWakeup = ref(true)
const continuousConversation = ref(false)

// 声音设置
const volume = ref(75)
const speechRate = ref(50) // 50% = 1.0x

const speechRateLabel = computed(() => {
  if (speechRate.value <= 25) return '0.75x'
  if (speechRate.value <= 50) return '1.0x'
  if (speechRate.value <= 75) return '1.25x'
  return '1.5x'
})
</script>

<template>
  <FixedAspectContainer 
    bg-color-class="bg-white"
    extra-class="font-display text-slate-900 antialiased overflow-y-auto no-scrollbar"
    :shadow="true"
  >

    <!-- Top Navigation Bar -->
    <header class="sticky mt-2 top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/60">
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
      <SettingsSection title="常规设置">
        <SettingsToggle
          v-model="voiceWakeup"
          icon="mic"
          label="语音唤醒"
          description="通过 '嘿，助手' 唤醒设备"
          :divider="true"
        />
        <SettingsToggle
          v-model="continuousConversation"
          icon="forum"
          label="连续对话"
          description="无需重复唤醒即可进行多轮对话"
        />
      </SettingsSection>

      <!-- 声音设置 -->
      <SettingsSection title="声音设置">
        <SettingsSlider
          v-model="volume"
          icon="volume_up"
          label="音量"
          :divider="true"
        />
        <SettingsSlider
          v-model="speechRate"
          icon="speed"
          label="语速"
          :display-value="speechRateLabel"
        />
      </SettingsSection>

      <!-- 其他 -->
      <SettingsSection title="其他">
        <SettingsLink icon="description" label="隐私权政策" :divider="true" />
        <SettingsLink icon="info" label="关于我们" />
      </SettingsSection>

    </main>
  </FixedAspectContainer>
</template>


