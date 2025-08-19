<template>
  <BaseBadge :color="color">
    {{ props.state }}
  </BaseBadge>
</template>

<script setup lang="ts">
import type { Assignment, ColorEnum } from '~/purple_client'

type Props = {
  state: Assignment["state"]
}

const props = defineProps<Props>()

const color = computed((): ColorEnum => {
  switch (props.state) {
    case undefined:
      return 'rose'
    case 'assigned':
      return 'blue'
    case 'in_progress':
      return 'indigo'
    case 'done':
      return 'green'
  }
  return 'gray'
})

</script>
