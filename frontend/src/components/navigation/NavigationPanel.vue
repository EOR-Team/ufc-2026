<template>
  <Transition name="slide-up">
    <div v-if="visible" class="navigation-panel absolute inset-x-4 top-1/2 -translate-y-1/2 z-40">
      <!-- 浮动面板容器 -->
      <div class="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full overflow-hidden">

        <!-- 面板标题栏 -->
        <div class="flex items-center justify-between px-4 py-3 bg-primary/5 border-b border-slate-200">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-lg">navigation</span>
            <h3 class="font-bold text-slate-800">导航控制</h3>
          </div>
          <button
            @click="handleClose"
            class="flex items-center justify-center w-8 h-8 rounded-full hover:bg-slate-100 transition-colors"
            aria-label="关闭导航面板"
          >
            <span class="material-symbols-outlined text-slate-500 text-sm">close</span>
          </button>
        </div>

        <!-- 面板内容区域 -->
        <div class="px-4 pt-3 pb-4" style="display: flex; flex-direction: column; gap: 20px;">

          <!-- 进度指示器 -->
          <div v-if="showProgress" class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-600">进度</span>
              <span class="font-medium text-primary">
                {{ currentCommandIndex + 1 }}/{{ totalCommands }}
              </span>
            </div>
            <div class="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-primary rounded-full transition-all duration-300"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
          </div>

          <!-- 当前指令显示 -->
          <div v-if="currentAction" class="bg-slate-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-primary text-base">
                  {{ getActionIcon(currentAction.orientation) }}
                </span>
                <span class="font-medium text-slate-800">{{ getActionLabel(currentAction.orientation) }}</span>
              </div>
              <span class="font-bold text-primary">{{ currentAction.distance }}单位</span>
            </div>
            <div v-if="currentCommandIndex !== null" class="mt-2 text-xs text-slate-500">
              指令 {{ currentCommandIndex + 1 }} of {{ totalCommands }}
            </div>
          </div>

          <!-- 导航控制按钮组 -->
          <div class="grid grid-cols-2 gap-3">
            <!-- 下一步按钮 -->
            <button
              @click="handleNextCommand"
              :disabled="isNextDisabled"
              class="flex items-center justify-center gap-2 py-1 px-2 bg-primary text-white font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span class="material-symbols-outlined text-base">arrow_forward</span>
              <span>下一步</span>
            </button>

            <!-- 检查位置按钮 -->
            <button
              @click="handleVerifyPosition"
              class="flex items-center justify-center gap-2 py-1 px-2 bg-primary hover:bg-primary/90 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span class="material-symbols-outlined text-base">check_circle</span>
              <span>检查位置</span>
            </button>
          </div>

          <!-- 状态信息 -->
          <div v-if="statusMessage" class="text-center text-sm" :class="statusMessageClass">
            <span class="material-symbols-outlined align-text-bottom text-base mr-1">
              {{ statusMessageIcon }}
            </span>
            {{ statusMessage }}
          </div>

          <!-- 验证结果 -->
          <div v-if="lastVerificationResult" class="mt-3 p-3 rounded-lg border" :class="verificationResultClass">
            <div class="flex items-start gap-2">
              <span class="material-symbols-outlined text-base mt-0.5">
                {{ lastVerificationResult.verified ? 'check_circle' : 'error' }}
              </span>
              <div class="flex-1">
                <div class="font-medium">{{ lastVerificationResult.verified ? '验证通过' : '验证失败' }}</div>
                <div class="text-xs mt-1 opacity-80">{{ lastVerificationResult.message }}</div>
                <div v-if="lastVerificationResult.confidence" class="text-xs mt-1">
                  置信度: {{ (lastVerificationResult.confidence * 100).toFixed(1) }}%
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref } from 'vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
    default: false
  },
  // 导航状态
  isActive: {
    type: Boolean,
    default: false
  },
  isPaused: {
    type: Boolean,
    default: false
  },
  currentCommandIndex: {
    type: Number,
    default: 0
  },
  totalCommands: {
    type: Number,
    default: 0
  },
  currentAction: {
    type: Object,
    default: null
  },
  lastVerificationResult: {
    type: Object,
    default: null
  },
  verificationPending: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'close',
  'next-command',
  'verify-position',
  'verify-position-with-image',
  'toggle-pause',
  'stop-navigation'
])

// 计算属性
const showProgress = computed(() => {
  return props.totalCommands > 0
})

const progressPercentage = computed(() => {
  if (props.totalCommands === 0) return 0
  return ((props.currentCommandIndex + 1) / props.totalCommands) * 100
})

const isNextDisabled = computed(() => {
  return !props.isActive || props.currentCommandIndex >= props.totalCommands - 1
})

const statusMessage = computed(() => {
  if (!props.isActive) return '导航未开始'
  if (props.isPaused) return '导航已暂停'
  if (props.verificationPending) return '位置验证中...'
  return '导航进行中'
})

const statusMessageClass = computed(() => {
  if (!props.isActive) return 'text-slate-500'
  if (props.isPaused) return 'text-amber-600'
  if (props.verificationPending) return 'text-blue-600'
  return 'text-primary'
})

const statusMessageIcon = computed(() => {
  if (!props.isActive) return 'info'
  if (props.isPaused) return 'pause_circle'
  if (props.verificationPending) return 'schedule'
  return 'navigation'
})

const verificationResultClass = computed(() => {
  if (!props.lastVerificationResult) return ''
  return props.lastVerificationResult.verified
    ? 'bg-green-50 border-green-200 text-green-800'
    : 'bg-red-50 border-red-200 text-red-800'
})

// 方法
function handleClose() {
  emit('close')
}

function handleNextCommand() {
  if (!isNextDisabled.value) {
    emit('next-command', props.currentCommandIndex)
  }
}

function handleVerifyPosition() {
  emit('verify-position')
}

function handleTogglePause() {
  emit('toggle-pause', !props.isPaused)
}

function handleStopNavigation() {
  // 可选：添加确认对话框
  if (confirm('确定要停止导航吗？')) {
    emit('stop-navigation')
  }
}

// 文件上传相关
const fileInput = ref(null)

function handleUploadImage() {
  // 触发隐藏的文件输入元素
  if (fileInput.value) {
    fileInput.value.click()
  }
}

async function handleFileSelected(event) {
  const file = event.target.files?.[0]
  if (!file) return

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }

  // 读取文件为base64
  try {
    const base64 = await readFileAsBase64(file)
    // 发射事件，传递base64图像数据
    emit('verify-position-with-image', base64)
  } catch (error) {
    console.error('Failed to read image file:', error)
    alert('读取图片失败')
  }
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      // 移除data:image/...;base64,前缀，只保留base64数据
      const result = reader.result
      const base64 = result.split(',')[1] || result
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

function getActionIcon(orientation) {
  const icons = {
    'straight': 'arrow_forward',
    'left': 'turn_left',
    'right': 'turn_right'
  }
  return icons[orientation] || 'directions'
}

function getActionLabel(orientation) {
  const labels = {
    'straight': '前进',
    'left': '左转',
    'right': '右转'
  }
  return labels[orientation] || '移动'
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.slide-up-enter-to,
.slide-up-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.navigation-panel {
  pointer-events: auto;
  /* 确保面板在遮罩层之上 */
  z-index: 50;
}

/* 按钮悬停效果 */
button:not(:disabled):hover {
  transform: translateY(-1px);
  transition: transform 0.2s ease;
}

button:active:not(:disabled) {
  transform: translateY(0);
}

/* 滚动条样式 */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}
</style>