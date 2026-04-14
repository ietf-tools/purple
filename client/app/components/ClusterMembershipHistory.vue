<template>
  <div>
    <h2 class="text-lg font-semibold mb-3">Cluster-Members History</h2>
    <div v-if="status === 'pending'" class="text-sm text-gray-500">Loading history...</div>
    <div v-else-if="status === 'error'" class="text-sm text-red-500">Failed to load history.</div>
    <div v-else-if="!entries.length" class="text-sm text-gray-500">No history recorded.</div>
    <table v-else class="w-full text-sm border-collapse">
      <thead>
        <tr class="border-b border-gray-300 dark:border-gray-600 text-left text-xs uppercase text-gray-500 dark:text-gray-400">
          <th class="py-2 pr-4 font-medium">Time</th>
          <th class="py-2 pr-4 font-medium">Document</th>
          <th class="py-2 pr-4 font-medium">Change</th>
          <th class="py-2 font-medium">By</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in entries" :key="`${entry.time}-${entry.draftName}-${entry.type}`"
          class="border-b border-gray-100 dark:border-gray-800">
          <td class="py-2 pr-4 text-gray-600 dark:text-gray-400 whitespace-nowrap">
            {{ entry.time ? new Date(entry.time).toLocaleString() : '—' }}
          </td>
          <td class="py-2 pr-4 font-mono">{{ entry.draftName ?? '—' }}</td>
          <td class="py-2 pr-4">
            <span :class="{
              'text-green-600 dark:text-green-400': entry.type === 'added',
              'text-red-600 dark:text-red-400': entry.type === 'removed',
              'text-blue-600 dark:text-blue-400': entry.type === 'reordered',
            }">{{ entry.type ?? '—' }}</span>
          </td>
          <td class="py-2">{{ (entry.by as any)?.name ?? entry.by ?? '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { ClusterMemberHistory } from '~/purple_client'

type Props = {
  clusterNumber: number
}

const props = defineProps<Props>()

const api = useApi()

const { data, status } = useAsyncData(
  () => `cluster-history-${props.clusterNumber}`,
  () => api.clustersHistoryList({ number: props.clusterNumber, limit: 200 }),
  { server: false, lazy: true }
)

const entries = computed<ClusterMemberHistory[]>(() => data.value?.results ?? [])
</script>
