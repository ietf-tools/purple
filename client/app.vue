<template>
  <div v-if="userStore.authenticated !== true" class="w-[3.5em] mt-2 mx-auto">
    <Icon
      name="ei:spinner-3"
      size="3.5em"
      class="animate-spin"
    />
    sdfsdsdsdfsdf
  </div>
  <NuxtLayout v-else>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>
