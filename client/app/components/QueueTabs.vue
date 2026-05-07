<template>
  <div class="flex justify-center items-center">
    <TabNav :tabs="tabs" :selected="props.currentTab" />
  </div>
</template>

<script setup lang="ts">
import type { QueueTabId } from '../utils/queue'
import { queueTabs } from '~/utils/queue'
import type { Tab } from '~/utils/tab'
import type { QueueCounts } from '~/purple_client'

type Props = {
  currentTab: QueueTabId
}

const props = defineProps<Props>()

const api = useApi()
const route = useRoute()

const { data: counts } = await useAsyncData(
  'queue-tab-counts',
  () => api.queueCounts(),
  {
    server: false,
    lazy: true,
    watch: [route],
    default: (): Partial<QueueCounts> => ({}),
  }
)

const tabs = computed<Tab[]>(() =>
  queueTabs.map(tab => {
    // map tab id to the corresponding count key
    // e.g. "pending-announcement" → "pendingAnnouncement"
    const countKey = tab.id.replace(/-([a-z])/g, (_, c) => c.toUpperCase()) as keyof QueueCounts
    return {
      ...tab,
      count: counts.value[countKey] ?? null,
    }
  })
)
</script>
