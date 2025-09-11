<template>
  <div class="lg:flex lg:items-center lg:justify-between text-gray-500 dark:text-neutral-300">
    <div class="min-w-0 flex-1">
      <h2 class="text-2xl font-bold leading-7 sm:truncate sm:text-3xl sm:tracking-tight">{{ title }}</h2>
      <div v-if="summary" class="mt-1 flex flex-col sm:mt-0 sm:flex-row sm:flex-wrap sm:space-x-6">
        <div class="mt-2 flex items-center text-sm">
          {{ summary }}
        </div>
      </div>
    </div>
    <div class="mt-5 flex lg:ml-4 lg:mt-0">
      <slot name="right"/>
    </div>
  </div>
</template>

<script setup lang="ts">

type Props = {
  title: string
  summary?: string
}

const props = defineProps<Props>()
</script>
