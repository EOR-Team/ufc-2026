<template>
  <div class="map-visualization relative w-full h-full">
    <!-- SVG 容器 -->
    <svg :width="width" :height="height" class="absolute inset-0">
      <!-- 渲染连接线 -->
      <g v-for="edge in highlightedMap.edges" :key="`${edge.source}-${edge.target}`">
        <line
          :x1="getNodeX(edge.source)"
          :y1="getNodeY(edge.source)"
          :x2="getNodeX(edge.target)"
          :y2="getNodeY(edge.target)"
          :class="edge.highlight ? 'map-edge-highlight' : 'map-edge-dimmed'"
          stroke-width="2"
        />
      </g>

      <!-- 渲染节点 -->
      <g v-for="node in highlightedMap.nodes" :key="node.id" class="cursor-pointer">
        <circle
          :cx="getNodeX(node.id)"
          :cy="getNodeY(node.id)"
          :r="nodeRadius"
          :class="node.highlight ? 'map-node-highlight' : 'map-node-dimmed'"
          @click="handleNodeClick(node)"
        />
        <text
          :x="getNodeX(node.id)"
          :y="getNodeY(node.id) + nodeRadius + 16"
          text-anchor="middle"
          class="text-xs fill-slate-600"
        >
          {{ node.name }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  highlightedMap: {
    type: Object,
    required: true
  },
  width: {
    type: Number,
    default: 600
  },
  height: {
    type: Number,
    default: 400
  },
  nodeRadius: {
    type: Number,
    default: 16
  }
});

const emit = defineEmits(['node-click']);

// 计算节点位置映射
const nodePositionMap = computed(() => {
  const map = {};
  if (props.highlightedMap && props.highlightedMap.nodes) {
    props.highlightedMap.nodes.forEach(node => {
      if (node.id !== undefined && node.x !== undefined && node.y !== undefined) {
        map[node.id] = { x: node.x, y: node.y };
      }
    });
  }
  return map;
});

function getNodeX(nodeId) {
  const pos = nodePositionMap.value[nodeId];
  return pos ? pos.x : props.width / 2;
}

function getNodeY(nodeId) {
  const pos = nodePositionMap.value[nodeId];
  return pos ? pos.y : props.height / 2;
}

function handleNodeClick(node) {
  emit('node-click', node);
}
</script>

<style scoped>
.map-node-highlight {
  fill: white;
  stroke: #4252b3; /* primary color */
  stroke-width: 2;
  filter: drop-shadow(0 2px 4px rgba(66, 82, 179, 0.2));
  transition: all 0.2s ease;
}

.map-node-highlight:hover {
  stroke-width: 3;
  filter: drop-shadow(0 3px 6px rgba(66, 82, 179, 0.3));
}

.map-node-dimmed {
  fill: #f1f5f9; /* slate-100 */
  stroke: #cbd5e1; /* slate-300 */
  stroke-width: 1;
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.map-node-dimmed:hover {
  opacity: 0.7;
}

.map-edge-highlight {
  stroke: #4252b3; /* primary color */
  stroke-width: 2;
  filter: drop-shadow(0 1px 2px rgba(66, 82, 179, 0.2));
}

.map-edge-dimmed {
  stroke: #cbd5e1; /* slate-300 */
  stroke-width: 1;
  opacity: 0.3;
}
</style>