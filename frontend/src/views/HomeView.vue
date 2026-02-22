<script setup>
import { useCounterStore } from '@/stores/counter'

const store = useCounterStore()
</script>

<template>
  <v-container class="py-10">
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">

        <h1 class="text-3xl font-bold text-center mb-2">
          UFC-2026 Frontend
        </h1>
        <p class="text-center text-gray-500 mb-8 text-sm">
          Vue3 · Pinia · Vuetify · Tailwind CSS · Vue Router
        </p>

        <!-- Pinia 计数器 -->
        <v-card class="mb-6" elevation="3" rounded="lg">
          <v-card-title class="text-lg font-semibold pt-5 pl-5">
            <v-icon class="mr-2">mdi-counter</v-icon>
            Pinia Counter
          </v-card-title>
          <v-card-text class="text-center py-6">
            <p class="text-5xl font-bold text-primary mb-1">{{ store.count }}</p>
            <p class="text-sm text-gray-400 mb-6">Double: {{ store.doubleCount }}</p>
            <div class="flex justify-center gap-3">
              <v-btn color="error" variant="tonal" icon="mdi-minus" @click="store.decrement" />
              <v-btn color="secondary" variant="tonal" icon="mdi-refresh" @click="store.reset" />
              <v-btn color="primary" variant="tonal" icon="mdi-plus" @click="store.increment" />
            </div>
          </v-card-text>
        </v-card>

        <!-- 技术栈标签 -->
        <v-card elevation="1" rounded="lg">
          <v-card-title class="text-base font-semibold pt-5 pl-5">
            <v-icon class="mr-2">mdi-shape-outline</v-icon>
            Tech Stack
          </v-card-title>
          <v-card-text>
            <div class="flex flex-wrap gap-2 mt-1">
              <v-chip color="green" variant="tonal" prepend-icon="mdi-vuejs">Vue 3</v-chip>
              <v-chip color="yellow" variant="tonal" prepend-icon="mdi-database">Pinia</v-chip>
              <v-chip color="blue" variant="tonal" prepend-icon="mdi-material-design">Vuetify 3</v-chip>
              <v-chip color="cyan" variant="tonal" prepend-icon="mdi-tailwind">Tailwind CSS</v-chip>
              <v-chip color="purple" variant="tonal" prepend-icon="mdi-routes">Vue Router</v-chip>
            </div>
          </v-card-text>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>
