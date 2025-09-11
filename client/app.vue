<template>
  <div v-if="!ifAuthRoute && userStore.authenticated === undefined" class="w-[3.5em] mt-2 mx-auto">
    <Icon
      name="ei:spinner-3"
      size="3.5em"
      class="animate-spin"
    />
  </div>
  <NuxtLayout v-else>
    <NuxtPage :key="$route.params.id" />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { testIsAuthRoute } from '~/utils/url'

const route = useRoute()
const userStore = useUserStore()

const ifAuthRoute = computed(() => testIsAuthRoute(route.fullPath))
</script>
