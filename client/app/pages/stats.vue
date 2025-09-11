<template>
  <table class="text-gray-900 dark:text-neutral-300">
    <thead>
    <tr>
      <th>Label</th>
      <th>Document</th>
      <th>Time applied</th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="stat of labelStats.labelStats" :key="`${stat.documentId}-${stat.labelId}`">
      <td>
        <RpcLabel
          v-if="labelById.hasOwnProperty(stat.labelId)"
          :label="labelById[stat.labelId]"/>
        <span v-else>?</span>
      </td>
      <td>{{ documentById[stat.documentId]?.name }}</td>
      <td>
        {{
          humanizeDuration(
            Duration.fromObject({ second: stat.seconds }).milliseconds,
            { largest: 1, round: true})
        }}
      </td>
    </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">

import { Duration } from 'luxon'
import humanizeDuration from 'humanize-duration'
import type { LabelStats } from '../purple_client'

const api = useApi()

// COMPUTED

const labelById = computed(() => Object.fromEntries(labels?.value.map(lbl => [lbl.id, lbl])))

const documentById = computed(() => Object.fromEntries(documents?.value.map(doc => [doc.id, doc])))

// DATA

const { data: labels } = await useAsyncData(() => api.labelsList(), { server: false, default: () => [] })

const { data: documents } = await useAsyncData(() => api.documentsList(), { server: false, default: () => [] })

const { data: labelStats } = await useAsyncData(
  () => api.statsLabels(), {
    server: false,
    default: () => ({ labelStats: [] }) as LabelStats
  }
)

</script>
