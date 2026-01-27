<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rawRfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="rawRfcToBeError" title="API Error">
        API error while requesting draft: {{ rawRfcToBeError }}
      </ErrorAlert>
      <div v-else
        class="mx-auto grid max-w-2xl grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">

        <!-- Document Info -->
        <DocInfoCard :rfc-to-be="rawRfcToBe" :draft-name="draftName" :refresh="rfcToBeRefresh" :is-read-only="Boolean(rawRfcToBe?.publishedAt)" />

        <div class="flex">
          <div class="flex flex-col">
            <h2 class="font-bold text-lg border border-gray-200 pl-6 pt-4 pb-2 text-black bg-white dark:text-white dark:bg-black rounded-t-xl">Complexities</h2>
            <div class="flex flex-row">
              <DocLabelsCard title="Other complexities" v-model="selectedLabelIds" :labels="labels1" />
              <DocLabelsCard title="Exceptions" v-model="selectedLabelIds" :labels="labels2" />
            </div>
          </div>
        </div>

        <DocLabelsCard title="Other labels" v-model="selectedLabelIds" :labels="labels3" />

        <div v-if="rawRfcToBe?.id" class="lg:col-span-full grid place-items-stretch">
          <DocumentDependencies v-model="relatedDocuments" :id="rawRfcToBe.id" :draft-name="draftName" :people="people"
            :cluster-number="rawRfcToBe.cluster?.number">
          </DocumentDependencies>
        </div>

        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <IANAActionsSummary v-if="rawRfcToBe && rawRfcToBe.name" :rfcToBe="rawRfcToBe"
            :on-success="rfcToBeRefresh" :name="rawRfcToBe.name" />
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

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { useAsyncData } from '#app'
import { snackbarForErrors } from "~/utils/snackbar"
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()
const snackbar = useSnackbar()

// COMPUTED

const currentTab: DocTabId = 'index'

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
    }
  },
  { deep: true }
)

const { data: people } = await useAsyncData(
  () => api.rpcPersonList(),
  { server: false, lazy: true, default: () => [] }
)

const { data: relatedDocuments } = await useReferencesForDraft(draftName.value)

useHead({
  title: draftName.value
})
</script>
