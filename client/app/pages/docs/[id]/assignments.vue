<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rawRfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="rawRfcToBeError" title="API Error">
        API error while requesting draft: {{ rawRfcToBeError }}
      </ErrorAlert>
      <div
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-2">

        <!-- Status summary -->
        <BaseCard class="grid place-items-stretch">
          <h2 class="sr-only">Status Summary</h2>
          <div class="px-0 pt-6 sm:px-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base font-semibold leading-7">Assignments</h3>
              <BaseButton v-if="!hasManualHold" btn-type="cancel" @click="setManualHold">Set Manual Hold</BaseButton>
              <BaseButton v-else btn-type="secondary" @click="clearManualHold">Clear Manual Hold</BaseButton>
            </div>
            <div class="text-sm font-medium">
              <div v-if="rfcToBeAssignments.length === 0">
                None
              </div>
              <dl v-else>
                <div v-for="assignment of rfcToBeAssignments" :key="assignment.id" class="py-1 grid grid-cols-2">
                  <dt><Anchor :href="teamMemberLink(assignment?.person)"><RpcPerson :person-id="assignment.person" :people="people" /></Anchor></dt>
                  <dd class="relative">
                    <BaseBadge :label="assignment.role" />
                    <AssignmentState :state="assignment.state" />
                    <template v-if="assignment.role === 'blocked' && assignment.state === 'in_progress' && blockingReasons.length > 0">
                      <ul class="mt-0.5 ml-4 text-xs text-gray-500 dark:text-neutral-400 list-disc list-inside">
                        <li v-for="br in blockingReasons" :key="br.name">
                          {{ br.name }}<span v-if="br.comment" class="italic"> — {{ br.comment }}</span>
                        </li>
                      </ul>
                    </template>
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
        </BaseCard>

        <HighlightSection id="edit-authors">
          <EditAuthors v-if="rfcToBe" :draft-name="draftName" v-model="rfcToBe" />
        </HighlightSection>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { useAsyncData } from '#app'
import { snackbarForErrors } from "~/utils/snackbar"
import { type DocTabId } from '~/utils/doc'
import { teamMemberLink }  from '~/utils/url'
import type { Assignment } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import { ManualHoldModal } from '#components'

const route = useRoute()
const api = useApi()
const snackbar = useSnackbar()
const { openOverlayModal } = inject(overlayModalKey)!

// COMPUTED

const currentTab: DocTabId = 'assignments'

const draftName = computed(() => route.params.id?.toString() ?? '')

const {
  data: commentList,
  pending: commentsPending,
  error: commentsError,
  refresh: commentsReload
} = await useCommentsForDraft(draftName.value)

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

const assignmentOrder = [
  'enqueuer',
  'formatting',
  'ref_checker',
  'first_editor',
  'second_editor',
  'final_review_editor',
  'publisher',
]

const rfcToBeAssignments = computed(() => {
  const forThisRfc = assignments.value.filter((a) => a.rfcToBe === rfcToBe.value?.id)

  const nonBlocked = forThisRfc
    .filter((a) => a.role !== 'blocked')
    .sort((a, b) => {
      const roleDiff = assignmentOrder.indexOf(a.role) - assignmentOrder.indexOf(b.role)
      if (roleDiff !== 0) return roleDiff
      return (a.id ?? 0) - (b.id ?? 0)
    })

  const blocked = forThisRfc
    .filter((a) => a.role === 'blocked')
    .sort((a, b) => (a.id ?? 0) - (b.id ?? 0))

  // Merge blocked into the role-ordered list at their chronological (ID) position
  const result: typeof forThisRfc = []
  let bi = 0
  for (const assignment of nonBlocked) {
    while (bi < blocked.length && (blocked[bi].id ?? 0) < (assignment.id ?? 0)) {
      result.push(blocked[bi++])
    }
    result.push(assignment)
  }
  while (bi < blocked.length) {
    result.push(blocked[bi++])
  }
  return result
})

const initialSelectedLabelIds = computed(() => {
  console.log("recomputing initial selected label ids")
  return [...(rawRfcToBe.value?.labels ?? [])]
})

const selectedLabelIds = ref([...initialSelectedLabelIds.value])

const blockingReasons = computed(() =>
  (rawRfcToBe.value?.blockingReasons ?? [])
    .filter((br) => br.resolved == null && br.reason?.name)
    .map((br) => ({ name: br.reason!.name, comment: br.comment ?? '' }))
)

const hasManualHold = computed(() =>
  (rawRfcToBe.value?.blockingReasons ?? []).some(
    (br) => br.reason?.slug === 'manual_hold' && br.resolved == null
  )
)

const setManualHold = () => {
  openOverlayModal({
    component: ManualHoldModal,
    componentProps: {
      onConfirm: async (comment: string) => {
        try {
          await api.documentsManualBlock({
            draftName: draftName.value,
            manualBlockRequestRequest: { comment },
          })
          await Promise.all([rfcToBeRefresh(), refreshAssignments()])
          snackbar.add({ type: 'success', title: 'Manual hold set', text: '' })
        } catch (e: unknown) {
          snackbarForErrors({ snackbar, error: e, defaultTitle: 'Failed to set manual hold' })
          throw e
        }
      },
    },
  }).catch(() => {})
}

const clearManualHold = async () => {
  try {
    await api.documentsManualUnblock({ draftName: draftName.value })
    await Promise.all([rfcToBeRefresh(), refreshAssignments()])
    snackbar.add({ type: 'success', title: 'Manual hold cleared', text: '' })
  } catch (e: unknown) {
    snackbarForErrors({ snackbar, error: e, defaultTitle: 'Failed to clear manual hold' })
  }
}

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
    }
  },
  { deep: true }
)

const { data: people } = await useAsyncData(
  () => api.rpcPersonList(),
  { server: false, lazy: true }
)

useHeadSafe({ title: draftName.value })
</script>
