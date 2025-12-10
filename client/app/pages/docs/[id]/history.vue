<template>
  <div>
    <header class="relative isolate">
      <div class="absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
        <div class="absolute left-16 top-full -mt-16 transform-gpu opacity-50 blur-3xl xl:left-1/2 xl:-ml-80">
          <div class="aspect-[1154/678] w-[72.125rem] bg-gradient-to-br from-[#FF80B5] to-[#9089FC]"
            style="clip-path: polygon(100% 38.5%, 82.6% 100%, 60.2% 37.7%, 52.4% 32.1%, 47.5% 41.8%, 45.2% 65.6%, 27.5% 23.4%, 0.1% 35.3%, 17.9% 0%, 27.7% 23.4%, 76.2% 2.5%, 74.2% 56%, 100% 38.5%)" />
        </div>
        <div class="absolute inset-x-0 bottom-0 h-px bg-gray-900/5" />
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div class="mx-auto flex max-w-2xl items-center justify-between gap-x-8 lg:mx-0 lg:max-w-none">

        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div>
        <!-- History -->
        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <h3 class="text-base font-semibold leading-7">
            History
            <Icon v-show="historyStatus === 'pending'" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          </h3>
          <div v-if="historyStatus === 'error'">
            <ErrorAlert title="Error loading history">
              <p v-if="historyError">{{ historyError }}</p>
              <p v-else>Please try reloading and report the error if it persists.</p>
            </ErrorAlert>
          </div>
          <div v-else-if="history && history.length > 0" class="flex">
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
                      {{ entry.by?.name ?? '(System)' }}
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

const route = useRoute()

// COMPUTED

const draftName = computed(() => route.params.id?.toString() ?? '')

const {
  data: history,
  error: historyError,
  status: historyStatus,
  refresh: historyRefresh
} = await useHistoryForDraft(draftName.value)
</script>
