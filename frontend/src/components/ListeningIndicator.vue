<script setup>
// 这个组件显示"正在倾听"的视觉指示器
</script>

<template>
  <div class="flex flex-col items-center justify-center relative bg-transparent">
    <!-- Pulsing rings -->
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div class="w-64 h-64 rounded-full bg-primary/10 animate-pulse-ring absolute"></div>
      <div class="w-64 h-64 rounded-full bg-primary/10 animate-pulse-ring absolute" style="animation-delay:1s"></div>
    </div>
    <!-- Audio wave bars -->
    <div class="relative z-10 flex items-center justify-center gap-2 h-32 bg-transparent">
      <div class="w-2 bg-primary rounded-full animate-wave-1 opacity-40"></div>
      <div class="w-2 bg-primary rounded-full animate-wave-2 opacity-60"></div>
      <div class="w-2 bg-primary rounded-full animate-wave-3 opacity-100"></div>
      <div class="w-2 bg-primary rounded-full animate-wave-4 opacity-60"></div>
      <div class="w-2 bg-primary rounded-full animate-wave-5 opacity-40"></div>
    </div>
    <p class="mt-3 text-primary font-medium tracking-wide text-sm uppercase bg-primary/10 backdrop-blur-sm rounded-full px-5 py-1 border border-primary/20">正在倾听...</p>
  </div>
</template>

<style scoped>
@keyframes pulse-ring {
  0%   { transform: scale(0.8); opacity: 0.5; }
  50%  { transform: scale(1.2); opacity: 0.3; }
  100% { transform: scale(0.8); opacity: 0.5; }
}
@keyframes wave-flow {
  0%   { height: 20px; }
  50%  { height: 80px; }
  100% { height: 20px; }
}
.animate-pulse-ring {
  animation: pulse-ring 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.animate-wave-1 { animation: wave-flow 1.2s ease-in-out infinite; }
.animate-wave-2 { animation: wave-flow 1.5s ease-in-out infinite; animation-delay: 0.2s; }
.animate-wave-3 { animation: wave-flow 1.0s ease-in-out infinite; animation-delay: 0.4s; }
.animate-wave-4 { animation: wave-flow 1.8s ease-in-out infinite; animation-delay: 0.1s; }
.animate-wave-5 { animation: wave-flow 1.3s ease-in-out infinite; animation-delay: 0.3s; }
</style>