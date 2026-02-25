<script setup>
import { RouterView } from 'vue-router'
import { nextTick } from 'vue'

const onBeforeEnter = () => {
  console.log('Transition: before enter');
}

const onAfterEnter = () => {
  console.log('Transition: after enter');
  // 确保过渡完成后触发布局更新
  nextTick(() => {
    // 触发 resize 事件，useViewportOverflow 监听此事件
    window.dispatchEvent(new Event('resize'));
  });
}

const onEnterCancelled = () => {
  console.log('Transition: enter cancelled');
}

const onBeforeLeave = () => {
  console.log('Transition: before leave');
}

const onAfterLeave = () => {
  console.log('Transition: after leave');
}

const onLeaveCancelled = () => {
  console.log('Transition: leave cancelled');
}
</script>

<template>
  <div id="app" class="flex justify-center items-center w-screen h-screen">
    <router-view v-slot="{ Component, route }">
      <transition
        :name="route.meta.transition || 'fade'"
        mode="out-in"
        @before-enter="onBeforeEnter"
        @after-enter="onAfterEnter"
        @enter-cancelled="onEnterCancelled"
        @before-leave="onBeforeLeave"
        @after-leave="onAfterLeave"
        @leave-cancelled="onLeaveCancelled"
      >
        <keep-alive>
          <component
            :is="Component"
            :key="route.path"
          />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>