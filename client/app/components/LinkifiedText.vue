<template>
  <div>
    <template v-for="(part, index) in parts" :key="index">
      <a
        v-if="part.href"
        :href="part.href"
        target="_blank"
        rel="noopener noreferrer"
        class="text-indigo-600 underline hover:text-indigo-500 dark:text-indigo-400"
        >{{ part.text }}</a
      >
      <template v-else>{{ part.text }}</template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { linkify } from '~/utils/linkify'

type Props = {
  text: string
}

const props = defineProps<Props>()

const parts = computed(() => linkify(props.text))
</script>
