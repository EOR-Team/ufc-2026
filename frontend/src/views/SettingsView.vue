<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import SettingsToggle from '@/components/settings/SettingsToggle.vue'
import SettingsSlider from '@/components/settings/SettingsSlider.vue'
import SettingsLink from '@/components/settings/SettingsLink.vue'
import SettingsSection from '@/components/settings/SettingsSection.vue'
import SettingsItem from '@/components/settings/SettingsItem.vue'

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

// 麦克风权限请求
const requestMicrophonePermission = async () => {
  try {
    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('❌ 您的浏览器不支持麦克风访问功能')
      return
    }

    // 请求麦克风权限
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 立即停止流（我们只需要权限，不需要实际录音）
    stream.getTracks().forEach(track => track.stop())

    // 权限获取成功
    alert('✅ 麦克风权限已获得！现在可以使用语音功能。')

  } catch (error) {
    // 权限获取失败
    const errorMessage = error.message || '未知错误'

    // 根据错误类型提供不同提示
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      alert(`❌ 麦克风权限被拒绝：${errorMessage}\n\n请在浏览器设置中启用麦克风权限。`)
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      alert(`❌ 未找到麦克风设备：${errorMessage}\n\n请确保设备连接了麦克风。`)
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      alert(`❌ 麦克风无法访问：${errorMessage}\n\n麦克风可能被其他应用占用。`)
    } else {
      alert(`❌ 麦克风权限获取失败：${errorMessage}`)
    }
  }
}
</script>

<template>
  <FixedAspectContainer 
    bg-color-class="bg-white"
    extra-class="font-display text-slate-900 antialiased overflow-y-auto no-scrollbar"
    :shadow="true"
  >

    <!-- Top Navigation Bar -->
    <header class="sticky mt-2 pb-1 top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/60">
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

      <!-- 权限设置 -->
      <SettingsSection title="权限设置">
        <SettingsItem
          icon="mic"
          label="麦克风权限"
          description="点击请求麦克风访问权限"
          :divider="true"
          row-class="py-3 cursor-pointer hover:bg-slate-50 active:bg-slate-100 transition-colors"
          @click="requestMicrophonePermission"
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


