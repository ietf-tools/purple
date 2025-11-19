<template>
  <li class="whitespace-nowrap inline-block">
    <a :href="`/docs/${props.document.name}`" :class="[
      ANCHOR_STYLE,
      'inline-block p-1 rounded-md'
    ]">
      <span v-if="props.document.rfcNumber">
        <span class="font-normal">RFC{{ NBSP }}</span>
        <span class="font-bold">{{ `${props.document.rfcNumber}:${SPACE} ` }}</span>
      </span>
      <span class="font-mono font-normal">
        {{ props.document.name }}
      </span>
    </a>
  </li>
</template>

<script setup lang="ts">
import type { ClusterMember } from '~/purple_client';

type Props = {
  document: ClusterMember
  headingLevel?: HeadingLevel
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 3 })

</script>
