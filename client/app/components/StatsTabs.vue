<template>
  <div class="flex justify-center items-center">
    <TabNav :tabs="statsTabs" :selected="props.currentTab" />
  </div>
</template>

<script setup lang="ts">
import type { Tab } from '~/utils/tab'

export type StatsTabId = 'time' | 'counts' | 'stream'

type Props = {
  currentTab: StatsTabId
}
const props = defineProps<Props>()

const statsTabs = [
  {
    id: 'time',
    name: 'Time',
    to: '/stats',
    icon: 'solar:clock-circle-bold-duotone'
  },
  {
    id: 'counts',
    name: 'Counts',
    to: '/stats/counts',
    icon: 'solar:documents-bold-duotone'
  },
  {
    id: 'stream',
    name: 'Stream',
    to: '/stats/stream',
    icon: 'solar:branching-paths-up-bold-duotone'
  }
] as const satisfies Tab[]
</script>
