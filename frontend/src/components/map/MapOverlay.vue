<template>
  <Transition name="fade">
    <div v-if="visible" class="map-overlay fixed inset-0 z-50">
      <!-- 背景遮罩 -->
      <div
        class="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
        @click="handleClose"
      />

      <!-- 地图容器 -->
      <div class="absolute inset-0 flex items-center justify-center p-6">
        <div class="relative bg-white rounded-2xl shadow-2xl max-w-4xl max-h-[80vh] w-full h-full overflow-hidden">
          <!-- 标题栏 -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-200">
            <h2 class="text-xl font-bold text-slate-800">导航地图</h2>
            <button
              @click="handleClose"
              class="flex items-center justify-center w-10 h-10 rounded-full hover:bg-slate-100 transition-colors"
              aria-label="关闭地图"
            >
              <span class="material-symbols-outlined text-slate-600">close</span>
            </button>
          </div>

          <!-- 地图内容 -->
          <div class="flex-1 p-6 overflow-auto">
            <div v-if="!highlightedMap || !highlightedMap.nodes || highlightedMap.nodes.length === 0"
                 class="flex items-center justify-center h-full">
              <div class="text-center text-slate-500">
                <span class="material-symbols-outlined text-4xl mb-4 block">map</span>
                <p>地图数据加载中...</p>
              </div>
            </div>
            <MapVisualization
              v-else
              :highlighted-map="highlightedMap"
              :width="600"
              :height="400"
              @node-click="handleNodeClick"
            />

            <!-- 图例 -->
            <div v-if="highlightedMap && highlightedMap.nodes && highlightedMap.nodes.length > 0"
                 class="mt-6 flex items-center justify-center gap-6">
              <div class="flex items-center gap-2">
                <div class="w-4 h-4 rounded-full bg-white border-2 border-primary shadow-sm"></div>
                <span class="text-sm text-slate-600">导航路径</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-4 h-4 rounded-full bg-slate-100 border border-slate-300 opacity-50"></div>
                <span class="text-sm text-slate-600">其他区域</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import MapVisualization from './MapVisualization.vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  highlightedMap: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'node-click']);

function handleClose() {
  emit('close');
}

function handleNodeClick(node) {
  emit('node-click', node);
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.map-overlay {
  pointer-events: auto;
}

/* 背景遮罩点击区域 */
.bg-black\/40 {
  pointer-events: auto;
  cursor: pointer;
}

/* 地图容器防点击穿透 */
.bg-white {
  pointer-events: auto;
}

/* 滚动区域样式 */
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