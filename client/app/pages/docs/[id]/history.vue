<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" @withdrawn="() => { rfcToBeRefresh(); historyRefresh() }" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="historyError" title="Error loading history">
        History: {{ historyError }}
      </ErrorAlert>

      <!-- History -->
      <BaseCard class="w-full lg:col-span-full grid place-items-stretch">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold leading-7">
            History
            <Icon v-show="historyStatus === 'pending'" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          </h3>
          <div class="flex gap-1 text-sm">
            <button v-for="f in FILTERS" :key="f.value" type="button"
              :class="['px-2.5 py-1 rounded-md border transition-colors', filter === f.value ? 'bg-violet-100 border-violet-400 text-violet-900 dark:bg-violet-900/30 dark:border-violet-500 dark:text-violet-200' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700']"
              @click="filter = f.value">
              {{ f.label }}
            </button>
          </div>
        </div>
        <div v-if="historyStatus === 'success'" class="w-full flex">
          <table class="w-full divide-y divide-gray-300">
            <thead class="bg-gray-50 dark:bg-neutral-800">
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold sm:pl-6">Date</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">By</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">Description</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="(entry, index) of filteredHistory" :key="index">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium sm:pl-6">
                  <time :datetime="DateTime.fromJSDate(entry.time).toString()">
                    {{ DateTime.fromJSDate(entry.time).toLocaleString(DateTime.DATE_MED) }}
                  </time>
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm">
                  <NuxtLink v-if="entry.by?.personId" :to="`/team/${entry.by.personId}`"
                    class="text-violet-900 hover:text-violet-500 dark:text-violet-300 hover:dark:text-violet-100">
                    {{ entry.by.name }}
                  </NuxtLink>
                  <span v-else>
                    {{ entry.by ? entry.by.name ? entry.by.name : '(unnamed)' : '(System)' }}
                  </span>
                </td>
                <td class="px-3 py-4 text-sm">{{ entry.desc }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()

const currentTab: DocTabId = 'history'

const draftName = computed(() => route.params.id?.toString() ?? '')

type FilterValue = 'all' | 'assignment' | 'cluster' | 'reference' | 'author' | 'metadata'
const FILTERS: { value: FilterValue; label: string; models: string[] }[] = [
  { value: 'all', label: 'All', models: [] },
  { value: 'metadata', label: 'Metadata', models: ['rfctobe'] },
  { value: 'assignment', label: 'Assignment', models: ['assignment', 'blocking_reason'] },
  { value: 'cluster', label: 'Cluster', models: ['cluster_member'] },
  { value: 'reference', label: 'Reference', models: ['reference'] },
  { value: 'author', label: 'Author', models: ['rfc_author'] },
]
const filter = ref<FilterValue>('all')

const {
  data: history,
  error: historyError,
  status: historyStatus,
  refresh: historyRefresh,
} = await useHistoryForDraft(draftName.value)

const filteredHistory = computed(() => {
  const entries = history.value ?? []
  if (filter.value === 'all') return entries
  const models = FILTERS.find(f => f.value === filter.value)?.models ?? []
  if (!models.length) return entries
  return entries.filter(e => e.model !== null && models.includes(e.model))
})

const { data: rfcToBe, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
    deep: true // author editing relies on deep reactivity
  }
)

useHeadSafe({ title: draftName.value })
</script>
