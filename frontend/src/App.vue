<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <v-app>
    <v-app-bar color="primary" elevation="2">
      <v-app-bar-title>UFC-2026</v-app-bar-title>
      <template #append>
        <v-btn :to="{ name: 'home' }" variant="text" prepend-icon="mdi-home">Home</v-btn>
        <v-btn :to="{ name: 'about' }" variant="text" prepend-icon="mdi-information">About</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>
