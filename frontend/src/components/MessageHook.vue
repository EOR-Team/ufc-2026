<template>
  <div class="message-hook mt-2 mb-4">
    <button
      @click="onClick"
      class="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 hover:bg-primary/20 text-primary font-medium rounded-full transition-colors"
    >
      <span class="material-symbols-outlined text-sm">map</span>
      <span>查看地图</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  onClick: {
    type: Function,
    required: true
  }
});
</script>

<style scoped>
.message-hook {
  display: flex;
  justify-content: center;
}

button {
  cursor: pointer;
  outline: none;
  border: none;
  transition: background-color 0.2s ease;
}

button:active {
  transform: translateY(1px);
}
</style>