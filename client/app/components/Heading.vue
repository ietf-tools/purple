<template>
  <component :is="`h${props.headingLevel}`"
    :class="[props.class, 'font-bold', { 'text-xl': props.headingLevel === 1, 'text-lg': props.headingLevel === 2, 'text-md': props.headingLevel === 3, 'text-sm': props.headingLevel === 4, 'text-xs': props.headingLevel === 5 || props.headingLevel === 6 }]">
    <slot />
  </component>
</template>

<script setup lang="ts">
import type { HeadingLevel } from '../utils/html'

type Props = {
  headingLevel: HeadingLevel
  class?: string
}

const props = defineProps<Props>()
</script>
