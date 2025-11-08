<template>
  <header class="border-b border-gray-200 px-4 py-5 sm:px-6">
    <div :class="[description ? '-mt-4': '-mt-2', '-ml-4 flex flex-wrap items-center justify-between sm:flex-nowrap']">
      <div :class="[description ? 'mt-4' : 'mt-2', 'ml-4']">
        <h3 class="text-base font-semibold leading-6 text-gray-900">
          {{ title }}
        </h3>
        <p
          v-if="description"
          class="mt-1 text-sm text-gray-500">
          {{ description }}
        </p>
      </div>
      <div
        v-if="$slots['actions']"
        class="ml-4 mt-4 flex-shrink-0">
        <slot name="actions"/>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string,
  description?: string
}>()
</script>
