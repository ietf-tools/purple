<template>
  <div>
    <StatsTabs current-tab="labels" />
    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <BaseCard class="w-full grid place-items-stretch">
        <h3 class="text-base font-semibold leading-7 mb-2">Time applied per label</h3>
        <table class="w-full text-sm text-gray-900 dark:text-neutral-300">
          <thead class="bg-gray-50 dark:bg-neutral-800">
          <tr>
            <th class="py-2 pl-4 pr-3 text-left font-semibold">Label</th>
            <th class="px-3 py-2 text-left font-semibold">Document</th>
            <th class="px-3 py-2 text-left font-semibold">Time applied</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
          <tr v-for="stat of labelStats.labelStats" :key="`${stat.documentId}-${stat.labelId}`">
            <td class="py-2 pl-4 pr-3">
              <RpcLabel
                v-if="labelById.hasOwnProperty(stat.labelId)"
                :label="labelById[stat.labelId]"/>
              <span v-else>?</span>
            </td>
            <td class="px-3 py-2">{{ documentById[stat.documentId]?.name }}</td>
            <td class="px-3 py-2">
              {{
                humanizeDuration(
                  Duration.fromObject({ second: stat.seconds }).milliseconds,
                  { largest: 1, round: true })
              }}
            </td>
          </tr>
          </tbody>
        </table>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">

import { Duration } from 'luxon'
import humanizeDuration from 'humanize-duration'
import type { LabelStats, PaginatedRfcToBeList } from '~/purple_client'

const api = useApi()

// DATA

const { data: labels } = await useAsyncData(() => api.labelsList(), { server: false, lazy: true, default: () => [] })

const { data: documents } = await useAsyncData(
  () => api.documentsList(),
  { server: false, lazy: true, default: () => ({ count: 0, results: [] }) as PaginatedRfcToBeList }
)

const { data: labelStats } = await useAsyncData(
  () => api.statsLabels(), {
    server: false,
    lazy: true,
    default: () => ({ labelStats: [] }) as LabelStats
  }
)

// COMPUTED

const documentById = computed(() => Object.fromEntries(documents.value.results.map(doc => [doc.id, doc])))

const labelById = computed(() => Object.fromEntries(labels?.value.map(lbl => [lbl.id, lbl])))

</script>
