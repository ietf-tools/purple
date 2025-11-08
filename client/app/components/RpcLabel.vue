<template>
  <BaseBadge :color="label?.color">
    <Icon v-if="label?.isException" class="mr-2" name="pajamas:warning"/>
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
