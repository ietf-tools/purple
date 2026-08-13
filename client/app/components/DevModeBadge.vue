<template>
  <span
    v-if="isDevMode"
    class="absolute right-3 top-1/2 -translate-y-1/2 rounded bg-amber-950 px-1.5 py-px text-[10px] font-bold uppercase leading-4 tracking-wide text-amber-50"
    title="Local development server (npm run dev)">
    Dev
  </span>
</template>

<script setup lang="ts">
import { isDevMode } from '~/utils/devMode'
</script>
