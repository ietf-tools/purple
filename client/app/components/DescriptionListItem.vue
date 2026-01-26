<template>
  <div :class="[
    'w-full',
    props.spacing === 'large' && 'px-4 py-3 sm:gap-4 sm:px-0',
    props.spacing === 'small' && 'px-1 py-0.5 sm:gap-0.5 sm:px-0',
  ]">
    <DescriptionListTerm v-if="term">
      {{ term }}
    </DescriptionListTerm>
    <slot />
    <DescriptionListDetails v-if="details">
      {{ details }}
    </DescriptionListDetails>
  </div>
</template>

<script setup lang="ts">
type Props = {
  term?: string,
  details?: string
  spacing?: 'large' | 'small'
}

const props = withDefaults(defineProps<Props>(), { spacing: "large" })
</script>
