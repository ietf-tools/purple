<template>
  <div class="px-4 py-3 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-0">
    <DescriptionListTerm v-if="term">
      {{ term }}
    </DescriptionListTerm>
    <slot/>
    <DescriptionListDetails v-if="details">
      {{ details }}
    </DescriptionListDetails>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  term?: string,
  details?: string
}>()
</script>
