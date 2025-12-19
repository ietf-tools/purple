<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rawRfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="rawRfcToBeError" title="API Error">
        API error while requesting draft: {{ rawRfcToBeError }}
      </ErrorAlert>
      <div v-else
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-2">

        <!-- Status summary -->
        <BaseCard class="grid place-items-stretch">
          <h2 class="sr-only">Status Summary</h2>
          <div class="px-0 pt-6 sm:px-6">
            <h3 class="text-base font-semibold leading-7">Assignments</h3>
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

        <EditAuthors v-if="rfcToBe" :draft-name="draftName" v-model="rfcToBe" />
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

const route = useRoute()
const api = useApi()
const snackbar = useSnackbar()

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

</script>
