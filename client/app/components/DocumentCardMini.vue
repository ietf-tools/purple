<template>
  <li class="whitespace-nowrap inline-block">
    <a :href="`/docs/${props.document.name}`" class="text-gray-700 dark:text-gray-200 font-semibold no-underline hover:underline focus:underline inline-block p-1 rounded-md">
      <span v-if="props.document.rfcNumber">
        <span class="font-normal">RFC{{ NBSP }}</span>
        <span class="font-semibold">{{ `${props.document.rfcNumber}:${SPACE} ` }}</span>
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
