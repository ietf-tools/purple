<template>
  <div class="flex justify-center items-center">
    <TabNav :tabs="statsTabs" :selected="props.currentTab" />
  </div>
</template>

<script setup lang="ts">
import type { Tab } from '~/utils/tab'

export type StatsTabId = 'queue' | 'labels'

type Props = {
  currentTab: StatsTabId
}
const props = defineProps<Props>()

const statsTabs = [
  {
    id: 'queue',
    name: 'Queue Summary',
    to: '/stats',
    icon: 'solar:chart-2-bold-duotone'
  },
  {
    id: 'labels',
    name: 'Labels',
    to: '/stats/labels',
    icon: 'pajamas:labels'
  }
] as const satisfies Tab[]
</script>
