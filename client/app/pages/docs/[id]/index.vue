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
          <div class="flex justify-between items-center gap-x-6 text-gray-900 dark:text-white">
            <div class="flex  items-center gap-x-6 justify-between">
              <Icon name="solar:document-text-line-duotone" class="w-10 h-10" />
              <h1>
                <span class="mt-1 text-xl font-semibold leading-6">
                  <span v-if="rfcToBe">{{ rfcToBe.name }}</span>
                </span>
              </h1>
            </div>
          </div>
          <div class="flex flex-row gap-5">
            <BaseButton @click="openEmailModal">New Email</BaseButton>
            <BaseButton @click="openAssignmentFinishedModal">Finish assignments</BaseButton>
            <BaseButton @click="openPublishModal">Publish</BaseButton>
          </div>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="rawRfcToBeError" title="API Error">
        API error while requesting draft: {{ rawRfcToBeError }}
      </ErrorAlert>
      <div v-else
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">

        <!-- Status summary -->
        <BaseCard class="lg:col-start-3 lg:row-start-1 lg:row-span-1 grid place-items-stretch">
          <h2 class="sr-only">Status Summary</h2>
          <div class="px-0 pt-6 sm:px-6">
            <h3 class="text-base font-semibold leading-7">Assignments</h3>
            <div class="text-sm font-medium">
              <div v-if="rfcToBeAssignments.length === 0">
                None
              </div>
              <dl v-else>
                <div v-for="assignment of rfcToBeAssignments" :key="assignment.id" class="py-1 grid grid-cols-2">
                  <dt>{{people.find(p => p.id === assignment.person)?.name ?? '(System)'}}</dt>
                  <dd class="relative">
                    <BaseBadge :label="assignment.role" />
                    <AssignmentState :state="assignment.state" />
                  </dd>
                </div>
              </dl>
            </div>
          </div>
          <div class="px-0 pt-6 sm:px-6">
            <h3 class="text-base font-semibold leading-7">Pending Activities</h3>
            <div class="text-sm font-medium">
              <div v-if="!rfcToBe || !rfcToBe.pendingActivities || rfcToBe.pendingActivities.length === 0">
                None
              </div>
              <dl v-else>
                <div v-for="pendingAct of rfcToBe?.pendingActivities" :key="pendingAct.slug"
                  class="py-1 grid grid-cols-2">
                  <dd class="relative">
                    <BaseBadge :label="pendingAct.slug" />
                  </dd>
                </div>
              </dl>
            </div>
          </div>
          <div class="px-4 py-6 sm:px-6 text-gray-900 dark:text-neutral-300">
            <h3 class="text-base font-semibold leading-7 ">Queue Information (mocked)</h3>
            <div class="text-sm font-medium">
              <dl>
                <div class="py-1 grid grid-cols-2">
                  <dt>Current State</dt>
                  <dd>EDIT-in-process</dd>
                </div>
                <div class="py-1 grid grid-cols-2">
                  <!-- Showing externalDeadline here - what about internal_goal? -->
                  <dt>Deadline</dt>
                  <dd>
                    <time v-if="rfcToBe?.externalDeadline" :datetime="rfcToBe.externalDeadline.toISODate()?.toString()">
                      {{ rfcToBe.externalDeadline.toLocaleString(DateTime.DATE_MED) }}
                    </time>
                    <span v-else>-</span>
                  </dd>
                </div>
                <div class="py-1 grid grid-cols-2">
                  <dt>Est. Completion</dt>
                  <dd>
                    <time datetime="2024-07-30">Jul 30, 2024</time>
                    <BaseBadge label="Overdue" color="red" />
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </BaseCard>

        <!-- Document Info -->
        <DocInfoCard :rfc-to-be="rawRfcToBe" :draft-name="draftName" :refresh="() => rfcToBeRefresh()" />

        <EditAuthors v-if="rfcToBe" :draft-name="draftName" v-model="rfcToBe" />

        <div class="flex w-full lg:col-span-2 space-x-4">
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

        <div v-if="rawRfcToBe?.id" class="lg:col-span-full grid place-items-stretch">
          <DocumentDependencies v-model="relatedDocuments" :id="rawRfcToBe.id" :draft-name="draftName" :people="people"
            :cluster-number="rawRfcToBe.cluster?.number">
          </DocumentDependencies>
        </div>

        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <IANAActionsSummary v-if="rawRfcToBe && rawRfcToBe.name" iana-action="iana-no-actions"
            :on-success="rfcToBeRefresh" :name="rawRfcToBe.name" />
        </BaseCard>

        <div class="lg:col-span-full">
          <DocumentFinalReviews :heading-level="4" :name="draftName" />
        </div>

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

        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <template #header>
            <CardHeader title="Comments (private)" />
          </template>
          <div v-if="rfcToBe && rfcToBe.id" class="flex flex-col items-center space-y-4">
            <RpcCommentTextarea v-if="rfcToBe" :draft-name="draftName" :reload-comments="commentsReload"
              class="w-4/5 min-w-100" />
            <DocumentComments :draft-name="draftName" :rfc-to-be-id="rfcToBe.id" :is-loading="commentsPending"
              :error="commentsError" :comment-list="commentList" :reload-comments="commentsReload"
              class="w-3/5 min-w-100" />
          </div>
        </BaseCard>

        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <template #header>
            <CardHeader title="Approval Logs (public)" />
          </template>
          <div v-if="rfcToBe && rfcToBe.id" class="flex flex-col items-center space-y-4">
            <RpcApprovalLogTextarea v-if="rfcToBe" :draft-name="draftName" :reload="approvalLogsListReload"
              class="w-4/5 min-w-100" />
            <DocumentApprovalLogs :draft-name="draftName" :rfc-to-be-id="rfcToBe.id"
              :is-loading="approvalLogsListPending" :error="approvalLogsListError" :comment-list="approvalLogsList"
              :reload="approvalLogsListReload" class="w-3/5 min-w-100" />
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { useAsyncData } from '#app'
import { snackbarForErrors } from "~/utils/snackbar"
import type { Assignment } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys';
import AssignmentFinishedModal from '../../../components/AssignmentFinishedModal.vue'
import EmailModal from '../../../components/EmailModal.vue'
import PublishModal from '../../../components/PublishModal.vue'

const route = useRoute()
const api = useApi()
const snackbar = useSnackbar()

// COMPUTED

const draftName = computed(() => route.params.id?.toString() ?? '')

const {
  data: commentList,
  pending: commentsPending,
  error: commentsError,
  refresh: commentsReload
} = await useCommentsForDraft(draftName.value)

const {
  data: approvalLogsList,
  pending: approvalLogsListPending,
  error: approvalLogsListError,
  refresh: approvalLogsListReload
} = await useAsyncData(
  `approval-log-${draftName.value}`,
  () => api.documentsApprovalLogsList({ draftName: draftName.value }),
  { server: false, lazy: true }
)

const {
  data: history,
  error: historyError,
  status: historyStatus,
  refresh: historyRefresh
} = await useHistoryForDraft(draftName.value)

const { data: rawRfcToBe, error: rawRfcToBeError, status: rfcToBeStatus, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
    deep: true // author editing relies on deep reactivity
  }
)

// todo retrieve assignments for a single draft more efficiently
const { data: assignments, refresh: refreshAssignments } = await useAsyncData(
  () => api.assignmentsList(),
  { server: false, lazy: true, default: () => [] as Assignment[] }
)

const rfcToBeAssignments = computed(() =>
  assignments.value.filter((a) => a.rfcToBe === rfcToBe.value?.id)
)

const initialSelectedLabelIds = computed(() => {
  console.log("recomputing initial selected label ids")
  return [...(rawRfcToBe.value?.labels ?? [])]
})

const selectedLabelIds = ref([...initialSelectedLabelIds.value])

const rfcToBe = computed((): CookedDraft | null => {
  if (rawRfcToBe.value) {
    if (rawRfcToBe.value.labels) {
      selectedLabelIds.value = [...rawRfcToBe.value.labels]
    }
    return {
      ...rawRfcToBe.value,
      externalDeadline:
        rawRfcToBe.value.externalDeadline
          ? DateTime.fromJSDate(rawRfcToBe.value.externalDeadline)
          : null
    }
  }
  return null
})

// DATA

const { data: labels, status: labelsStatus } = await useLabels()

const labels1 = computed(() =>
  labels.value.filter((label) => label.used && label.isComplexity && !label.isException)
)

const labels2 = computed(() =>
  labels.value.filter((label) => label.used && label.isComplexity && label.isException)
)

const labels3 = computed(
  () => labels.value.filter((label) => label.used && !label.isComplexity)
)

watch(
  selectedLabelIds,
  async () => {
    // spreading to ensure ref proxy objects provide primitive number values and not a wrapped proxy thing that would confuse difference()
    const initialValues = new Set([...initialSelectedLabelIds.value])
    const selectedValues = new Set([...selectedLabelIds.value])

    const areSetsSame = (a: Set<number>, b: Set<number>): boolean =>
      a.size === b.size &&
      [...a].every((x) => b.has(x));

    if (areSetsSame(initialValues, selectedValues)) {
      console.log("No change in label ids. Not saving. ", initialValues, ' vs ', selectedValues)
      return
    }

    console.log("Changes found in label ids so saving: ",  initialValues, ' vs ', selectedValues)

    try {
      await api.documentsPartialUpdate({
        draftName: draftName.value,
        patchedRfcToBeRequest: { labels: selectedLabelIds.value }
      })

      snackbar.add({
        type: 'success',
        title: `Updated labels for "${draftName.value}"`,
        text: ''
      })

    } catch (e: unknown) {
      snackbarForErrors({
        snackbar,
        defaultTitle: `Unable to update labels for "${draftName.value}"`,
        error: e
      })
    } finally {
      // Refresh history and assignments
      await Promise.all([
        historyRefresh(),
        refreshAssignments()
      ])
    }
  },
  { deep: true }
)

const { data: people } = await useAsyncData(
  () => api.rpcPersonList(),
  { server: false, lazy: true, default: () => [] }
)

const { data: relatedDocuments } = await useReferencesForDraft(draftName.value)

const overlayModal = inject(overlayModalKey)

const openAssignmentFinishedModal = () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal, closeOverlayModal } = overlayModal

  if (!rfcToBeAssignments.value || rfcToBeAssignments.value.length === 0) {
    snackbar.add({
      type: 'warning',
      title: `Still loading assignments...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  if (!people.value || people.value.length === 0) {
    snackbar.add({
      type: 'warning',
      title: `Still loading people...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  if (!rfcToBe.value) {
    snackbar.add({
      type: 'warning',
      title: `Still loading RFC details...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  openOverlayModal({
    component: AssignmentFinishedModal,
    componentProps: {
      assignments: rfcToBeAssignments.value,
      people: people.value,
      rfcToBe: rfcToBe.value,
      onSuccess: () => {
        refreshAssignments()
      }
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

const { data: mailTemplateList, error: mailTemplateListError, status: mailTemplateListStatus } = await useAsyncData(
  () => `mail-template-${rawRfcToBe.value?.id}`,
  async () => {
    if (!rawRfcToBe.value) {
      return []
    }
    const { id } = rawRfcToBe.value
    if (id === undefined) {
      console.warn('Expected rfcToBe to have id')
      return []
    }
    return api.mailtemplateList({
      rfctobeId: id
    })
  }, {
  server: false,
  lazy: true
}
)

const openEmailModal = async () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  if (!rawRfcToBe.value) {
    snackbar.add({
      type: 'warning',
      title: `Still loading RFC authors...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  if (!people.value || people.value.length === 0) {
    snackbar.add({
      type: 'warning',
      title: `Still loading people...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  if (!mailTemplateList.value && mailTemplateListStatus.value === 'pending') {
    snackbar.add({
      type: 'warning',
      title: `Still loading mail templates...`,
      text: 'Try again in a few seconds'
    })
    return
  }

  if (mailTemplateListStatus.value === 'error') {
    snackbar.add({
      type: 'error',
      title: `Failed to load mail templates. Reload page then try again`,
      text: mailTemplateListError.value?.message ?? ''
    })
    return
  }

  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: EmailModal,
    componentProps: {
      mailTemplates: mailTemplateList.value,
      onSuccess: () => {
        historyRefresh()
      }
    },
    mode: 'overlay',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

const openPublishModal = () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  if (labelsStatus.value !== 'success') {
    snackbar.add({ type: "warning", title: "Still loading labels", text: "Try again soon" })
    return
  }

  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: PublishModal,
    componentProps: {
      rfcToBe: rfcToBe.value,
      labels: labels.value,
      onSuccess: () => {
        historyRefresh()
      }
    },
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
