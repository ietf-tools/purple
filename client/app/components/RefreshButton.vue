<template>
  <button type="button" class="btn-secondary">
    <span class="sr-only">Refresh</span>
    <Icon
      name="solar:refresh-line-duotone" size="1.5em" :class="[pending ? 'animate-spin text-orange-600' : 'text-gray-500 dark:text-neutral-300']"
      aria-hidden="true"
      @click="$emit('refresh')"/>
  </button>
</template>

<script setup lang="ts">
type Props = {
  pending?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pending: false
})

defineEmits(['refresh'])
</script>
