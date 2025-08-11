<template>
  <div>
    <header class="relative isolate">
      <div class="absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
        <div class="absolute left-16 top-full -mt-16 transform-gpu opacity-50 blur-3xl xl:left-1/2 xl:-ml-80">
          <div
            class="aspect-[1154/678] w-[72.125rem] bg-gradient-to-br from-[#FF80B5] to-[#9089FC]"
            style="clip-path: polygon(100% 38.5%, 82.6% 100%, 60.2% 37.7%, 52.4% 32.1%, 47.5% 41.8%, 45.2% 65.6%, 27.5% 23.4%, 0.1% 35.3%, 17.9% 0%, 27.7% 23.4%, 76.2% 2.5%, 74.2% 56%, 100% 38.5%)"/>
        </div>
        <div class="absolute inset-x-0 bottom-0 h-px bg-gray-900/5"/>
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div class="mx-auto flex max-w-2xl items-center justify-between gap-x-8 lg:mx-0 lg:max-w-none">
          <div class="flex items-center gap-x-6 text-gray-900 dark:text-white">
            <Icon name="solar:document-text-line-duotone" class="w-10 h-10"/>
            <h1>
              <div class="mt-1 text-xl font-semibold leading-6">
                <span v-if="draft">{{ draft.name }}-{{ draft.rev }}</span>
              </div>
            </h1>
          </div>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">

        <!-- Status summary -->
        <BaseCard class="lg:col-start-3 lg:row-start-1 lg:row-span-1 grid place-items-stretch">
          <h2 class="sr-only">Status Summary</h2>
          <div class="px-4 pt-6 sm:px-6">
            <h3 class="text-base font-semibold leading-7">Current Assignments</h3>
            <div class="mx-4 text-sm font-medium ">
              <div v-if="draftAssignments.length === 0">
                None
              </div>
              <dl v-else>
                <div
                  v-for="assignment of draftAssignments"
                  :key="assignment.id"
                  class="py-1 grid grid-cols-2">
                  <dt>{{ people.find(p => p.id === assignment.person)?.name }}</dt>
                  <dd class="relative">
                    <BaseBadge class="absolute right-0" :label="assignment.role"/>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
          <div class="px-4 py-6 sm:px-6 text-gray-900 dark:text-neutral-300">
            <h3 class="text-base font-semibold leading-7 ">Queue Information (mocked)</h3>
            <div class="mx-4 text-sm font-medium">
              <dl>
                <div class="py-1 grid grid-cols-2">
                  <dt>Current State</dt>
                  <dd>EDIT-in-process</dd>
                </div>
                <div class="py-1 grid grid-cols-2">
                  <!-- Showing externalDeadline here - what about internal_goal? -->
                  <dt>Deadline</dt>
                  <dd>
                    <time v-if="draft?.externalDeadline" :datetime="draft.externalDeadline.toISODate()?.toString()">
                      {{ draft.externalDeadline.toLocaleString(DateTime.DATE_MED) }}
                    </time>
                    <span v-else>-</span>
                  </dd>
                </div>
                <div class="py-1 grid grid-cols-2">
                  <dt>Est. Completion</dt>
                  <dd>
                    <time datetime="2024-07-30">Jul 30, 2024</time>
                    <BaseBadge label="Overdue" color="red"/>
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </BaseCard>

        <!-- Document Info -->
        <DocInfoCard :draft="rawDraft"/>

        <EditAuthors v-if="draft" :draft-name="draftName" v-model="draft"/>

        <!-- Labels -->
        <BaseCard class="lg:col-start-3 lg:row-start-2 lg:row-span-1 grid place-items-stretch">
          <h3 class="text-base font-semibold leading-7">Labels</h3>
          <div class="flex">
            <div v-for="lbl of appliedLabels" :key="lbl.id" class="flex-shrink-0 p-1">
              <RpcLabel :label="lbl"/>
            </div>
          </div>
          <RpcLabelPicker
            :labels="labels" :model-value="draft?.labels" item-label="slug"
            @update:model-value="saveLabels"/>
        </BaseCard>

        <div class="flex w-full space-x-4">
          <div class="flex flex-col">
            <h2 class="font-bold text-lg border border-gray-200 pl-6 pt-4 pb-2 bg-white rounded-t-xl">Complexities</h2>
            <div class="flex flex-row">
              <DocLabelsCard title="Other complexities" v-model="selectedLabelIds" :labels="labels1" />
              <DocLabelsCard title="Exceptions" v-model="selectedLabelIds" :labels="labels2" />
            </div>
          </div>
          <div class="flex flex-col">
            <DocLabelsCard title="Other labels" v-model="selectedLabelIds" :labels="labels3" />
          </div>
        </div>

        <!-- History -->
        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <h3 class="text-base font-semibold leading-7">History</h3>
          <div class="flex">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50 dark:bg-neutral-800">
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold sm:pl-6">Date</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">By</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold">Description</th>
              </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
              <tr v-for="entry of draft?.history ?? []" :key="entry.id">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium sm:pl-6">
                  <time :datetime="DateTime.fromJSDate(entry.time).toString()">
                    {{ DateTime.fromJSDate(entry.time).toLocaleString(DateTime.DATE_MED) }}
                  </time>
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm">
                  <NuxtLink
                    v-if="entry.by?.personId"
                    :to="`/team/${entry.by.personId}`"
                    class="text-violet-900 hover:text-violet-500 dark:text-violet-300 hover:dark:text-violet-100">
                    {{ entry.by.name }}
                  </NuxtLink>
                  <span v-else>
                        {{ entry.by?.name }}
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
const api = useApi()

// COMPUTED

const draftName = computed(() => route.params.id.toString())

const { data: rawDraft, pending: draftPending, refresh: draftRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  { server: false }
)

const appliedLabels = computed(() => labels.value.filter((lbl) => rawDraft.value?.labels.includes(lbl.id)))

const draftAssignments = computed(() => assignments.value.filter((a) => a.rfcToBe === draft.value?.id))

const draft = computed(() => {
  if (rawDraft.value) {
    return {
      ...rawDraft.value,
      externalDeadline:
        rawDraft.value.externalDeadline
          ? DateTime.fromJSDate(rawDraft.value.externalDeadline)
          : null
    }
  }
  return null
})

// DATA

const { data: labels } = await useAsyncData(() => api.labelsList(), { server: false, default: () => [] })

const labels1 = computed(() =>
  labels.value.filter((label) => label.isComplexity && !label.isException)
)

const labels2 = computed(() =>
  labels.value.filter((label) => label.isComplexity && label.isException)
)

const labels3 = computed(
  () => labels.value.filter((label) => !label.isComplexity)
)

const selectedLabelIds = ref(draft.value?.labels ?? [])

watch(
  selectedLabelIds,
  async () => api.documentsPartialUpdate({
    draftName: draftName.value,
    patchedRfcToBe: {
      labels: selectedLabelIds.value,
    }
  }),
  { deep: true }
)


// todo retrieve assignments for a single draft more efficiently
const { data: assignments } = await useAsyncData(
  () => api.assignmentsList(),
  { server: false, default: () => [] }
)

const { data: people } = await useAsyncData(
  () => api.rpcPersonList(),
  { server: false, default: () => [] }
)

async function saveLabels (labels: number[]) {
  if (!draftPending.value) {
    await api.documentsPartialUpdate({
      draftName: draft.value?.name ?? '',
      patchedRfcToBe: { labels }
    })
  }
  draftRefresh()
}
</script>
