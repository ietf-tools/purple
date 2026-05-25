<template>
  <div class="mt-8">
    <h2 class="text-sm font-semibold text-gray-700 dark:text-neutral-400 mb-3">{{ title }}</h2>
    <p v-if="labels.length === 0" class="text-sm text-gray-500 italic">(None)</p>
    <div v-else class="grid grid-cols-4 gap-3">
      <div
        v-for="label in labels"
        :key="label.slug"
        class="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3 shadow-sm dark:border-neutral-700 dark:bg-neutral-800"
      >
        <RpcLabel :label="label" />
        <Icon
          name="circum:edit"
          class="ml-3 shrink-0 text-indigo-600 hover:text-indigo-900 cursor-pointer"
          @click="$emit('edit', label)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Label } from '~/purple_client'

defineProps<{
  title: string
  labels: Label[]
}>()

defineEmits<{
  edit: [label: Label]
}>()
</script>
