<script setup>
import { useRouter } from 'vue-router'
import FixedAspectContainer from '@/components/FixedAspectContainer.vue'
import SettingsToggle from '@/components/settings/SettingsToggle.vue'
import SettingsSection from '@/components/settings/SettingsSection.vue'
import SettingsItem from '@/components/settings/SettingsItem.vue'
import { useApiStore } from '@/stores/api.js'

const router = useRouter()
const apiStore = useApiStore()

const requestMicrophonePermission = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('❌ 您的浏览器不支持麦克风访问功能')
      return
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach(track => track.stop())
    alert('✅ 麦克风权限已获得！现在可以使用语音功能。')
  } catch (error) {
    const errorMessage = error.message || '未知错误'
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

      <!-- 权限设置 -->
      <SettingsSection title="权限设置">
        <SettingsItem
          icon="mic"
          label="麦克风权限"
          description="点击请求麦克风访问权限"
          row-class="py-3 cursor-pointer hover:bg-slate-50 active:bg-slate-100 transition-colors"
          @click="requestMicrophonePermission"
        />
      </SettingsSection>

      <!-- 模型设置 -->
      <SettingsSection title="模型设置">
        <SettingsToggle
          v-model="apiStore.onlineModelEnabled"
          icon="cloud"
          label="使用在线模型"
          description="启用后使用云端模型推理，关闭则使用本地离线模型"
        />
      </SettingsSection>

    </main>
  </FixedAspectContainer>
</template>
