<template>
  <div class="rounded-lg bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5 p-6">
    <button
      type="button"
      class="flex w-full items-center gap-2 text-left"
      :aria-expanded="!collapsed"
      :aria-controls="panelId"
      @click="collapsed = !collapsed">
      <Icon
        name="heroicons:chevron-right"
        class="h-4 w-4 shrink-0 text-gray-500 transition-transform"
        :class="collapsed ? '' : 'rotate-90'"
        aria-hidden="true" />
      <h2 class="text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-200">
        {{ title }}
      </h2>
      <span
        v-if="count !== undefined"
        class="rounded-full bg-gray-100 px-2 text-xs text-gray-600 dark:bg-neutral-800 dark:text-neutral-300">
        {{ count }}
      </span>
    </button>
    <div v-show="!collapsed" :id="panelId">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useLocalStorage } from '@vueuse/core'

const props = defineProps<{
  title: string
  /** localStorage key; the collapsed state survives reloads */
  storageKey: string
  count?: number
}>()

const collapsed = useLocalStorage(`${props.storageKey}-collapsed`, false)
const panelId = useId()
</script>
