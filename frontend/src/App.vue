<script setup>
import { RouterView } from 'vue-router'

const onBeforeEnter = () => {
  console.log('Transition: before enter');
}

const onAfterEnter = () => {
  console.log('Transition: after enter');
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
        name="fade" 
        mode="out-in"
        :css="true"
        @before-enter="onBeforeEnter"
        @after-enter="onAfterEnter"
        @enter-cancelled="onEnterCancelled"
        @before-leave="onBeforeLeave"
        @after-leave="onAfterLeave"
        @leave-cancelled="onLeaveCancelled"
      >
        <component 
          :is="Component" 
          :key="route.path"
        />
      </transition>
    </router-view>
  </div>
</template>