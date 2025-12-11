<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="historyError" title="Error loading history">
        History: {{ historyError }}
      </ErrorAlert>
      <div
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">

        <!-- History -->
        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <h3 class="text-base font-semibold leading-7">
            History
            <Icon v-show="historyStatus === 'pending'" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          </h3>
          <div v-if="historyStatus === 'success'" class="flex">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50 dark:bg-neutral-800">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold sm:pl-6">Date</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">By</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">Description</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="entry of history ?? []" :key="entry.id">
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
                      {{ entry.by ? entry.by.name ? entry.by.name : '(nnnamed)' : '(System)' }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">{{ entry.desc }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { useAsyncData } from '#app'
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()

// COMPUTED

const currentTab: DocTabId = 'history'

const draftName = computed(() => route.params.id?.toString() ?? '')

const {
  data: history,
  error: historyError,
  status: historyStatus,
  refresh: historyRefresh
} = await useHistoryForDraft(draftName.value)

const { data: rfcToBe, error: rfcToBeError, status: rfcToBeStatus, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
    deep: true // author editing relies on deep reactivity
  }
)

</script>
