<template>
  <BaseBadge :color="label?.color">
    <Icon v-if="label?.isException" class="mr-1" name="pajamas:warning" title="Exception" />
    <Icon v-if="label?.isComplexity" class="mr-1" name="uil:layer-group" title="Complexity" />
    <Icon v-if="label?.isPublic" class="mr-1" name="uil:globe" title="Public" />
    {{ label?.slug }}
  </BaseBadge>
</template>

<script setup lang="ts">
import type { Label } from '~/purple_client'

type Props = {
  label?: Label
}

const props = defineProps<Props>()
</script>
