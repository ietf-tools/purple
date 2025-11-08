<template>
  <input
    type="checkbox"
    aria-hidden="true"
    inert
    tabindex="-1"
    class="border-gray-300 dark:border-neutral-500 text-violet-600 dark:text-violet-500 hover:border-violet-400 dark:hover:border-violet-500 focus:ring-violet-600 dark:focus:ring-violet-500 h-4 w-4 bg-white dark:bg-neutral-900 rounded border-2"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
// A checkbox that is:
// * visible
// * but not interactive, focusable, or listenable to screenreaders
//
// The term 'inert' comes from https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/inert
</script>
