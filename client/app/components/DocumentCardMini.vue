<template>
  <Anchor
    :href="`/docs/${props.document.name}`"
    :class="[
      'font-semibold no-underline hover:underline focus:underline inline-block p-1 rounded-md',
      props.document.disposition === 'published'
        ? 'text-gray-400 bg-gray-100 dark:text-gray-500 dark:bg-gray-800'
        : props.document.isReceived === false
          ? 'bg-[#ee828d] text-white'
          : 'text-gray-700 dark:text-gray-200'
    ]"
  >
    <span v-if="props.document.rfcNumber">
      <span class="font-normal">RFC{{ NBSP }}</span>
      <span class="font-semibold">{{ `${props.document.rfcNumber}:${SPACE} ` }}</span>
    </span>
    <span class="font-mono font-normal">
      {{ props.document.name }}
    </span>
  </Anchor>
</template>

<script setup lang="ts">
import { Anchor } from '#components'
import type { ClusterMember } from '~/purple_client';

type Props = {
  document: ClusterMember
  headingLevel?: HeadingLevel
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 3 })
</script>
