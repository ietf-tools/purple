<template>
  <th
    class="px-1 first:pl-3 last:pr-3 py-3.5 text-left text-sm flex-inline content-start font-semibold text-gray-900 dark:text-neutral-400"
    :aria-sort="props.sortDirection ? props.sortDirection === 'asc' ? 'ascending' : 'descending' : undefined">
    <span v-if="props.isSortable === undefined || props.isSortable === false">
      <slot />
    </span>
    <button v-else type="button" class="cursor-pointer text-gray-400 dark:text-neutral-400 hover:text-gray-900 focus:text-gray-900 dark:hover:text-gray-200 dark:focus:text-gray-200" v-bind="$attrs">
      <span class="text-gray-800 dark:text-neutral-400"><slot /></span>
      <Icon v-if="props.sortDirection === 'asc'" name="uil:arrow-up" class="text-gray-900 dark:text-gray-100 h-4 text-lg -mt-0.5" />
      <Icon v-else-if="props.sortDirection === 'desc'" name="uil:arrow-down" class="text-gray-900 dark:text-gray-100 h-4 text-lg -mt-0.5" />
      <Icon v-else-if="isSortable" name="heroicons:arrows-up-down" />
    </button>
  </th>
</template>

<script setup lang="ts">
type Props = {
  isSortable?: boolean
  sortDirection?: false | "desc" | "asc"
}

const props = defineProps<Props>()
</script>
