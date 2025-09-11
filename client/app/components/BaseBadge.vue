<template>
  <span
    :class="[
      'inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset',
      badgeColors[props.color]
    ]"
  >
    {{ props.label }}
    <!-- @slot Optional badge content. Appears after the label, if any. -->
    <slot/>
  </span>
</template>

<script setup lang="ts">
import type { ColorEnum } from '~~/purple_client'
import { badgeColors } from '~/utils/badge'

type Props = {
  /**
   * Label text
   */
  label?: string
  /**
   * Tailwind color name
   */
  color?: ColorEnum
}

const props = withDefaults(defineProps<Props>(), {
  color: 'violet',
  label: ''
})

</script>
