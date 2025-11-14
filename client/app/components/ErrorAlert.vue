<template>
  <div class="rounded-md bg-red-50 p-4 dark:bg-red-500/15 dark:outline dark:outline-red-500/25">
    <div class="flex">
      <div class="ml-3">
        <h3 v-if="props.title" class="text-sm font-medium text-red-800 dark:text-red-200">{{ props.title }}</h3>
        <div class="mt-2 text-sm text-red-700 dark:text-red-200/80">
          <slot/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type Props = { title?: string }
const props = withDefaults(defineProps<Props>(), { title: 'Error' })
</script>
