<template>
  <div>
    <TitleBlock class="pb-3" :title="`Prep for Queue: ${rfcToBe?.name || '&hellip;'}`"
      summary="Ready the incoming document for the editing queue." />

    <div class="space-y-4">
      <div v-if="rfcToBeError" class="bg-red-300 px-4 py-2 mb-4">
        API error while requesting draft: {{ rfcToBeError }}
      </div>

      <div class="flex flex-row">
        <DocInfoCard :rfc-to-be="rfcToBe" />
        <EditAuthors v-if="rfcToBe" :draft-name="id" v-model="rfcToBe"/>
      </div>

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
      <div v-if="rfcToBe?.id">
        <DocumentDependencies v-model="relatedDocuments"
                              :id="rfcToBe.id"
                              :draft-name="id"
                              :cluster-number="rfcToBe.cluster?.number">
        </DocumentDependencies>
      </div>
      <BaseCard>
        <template #header>
          <CardHeader title="Comments" />
        </template>
        <div v-if="rfcToBe && rfcToBe.id" class="flex flex-col items-center space-y-4">
          <RpcCommentTextarea v-if="rfcToBe" :draft-name="id" :reload-comments="commentsReload" class="w-4/5 min-w-100" />
          <DocumentComments :draft-name="id" :rfc-to-be-id="rfcToBe.id" :is-loading="commentsPending"
            :error="commentsError" :comment-list="commentList" :reload-comments="commentsReload"
            class="w-3/5 min-w-100" />
        </div>
      </BaseCard>

      <div class="justify-end flex space-x-4">
        <BaseButton btn-type="default">Document has exceptions&mdash;escalate</BaseButton>
        <BaseButton btn-type="default" @click="addToQueue">
          <Icon
            v-if="isAddingToQueue"
            name="ei:spinner-3"
            size="1em"
            class="ml-1 animate-spin"
          />
          Add to queue
        </BaseButton>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import type { RfcToBe } from '~/purple_client'
import { snackbarForErrors } from '~/utils/snackbar'
import { QUEUE_QUEUE_PATH } from '~/utils/url'

const route = useRoute()
const api = useApi()

const id = computed(() => route.params.id?.toString() ?? '')

const rfcToBeKey = computed(() => `rfcToBe-${id.value}`)

const { data: rfcToBe, error: rfcToBeError } = await useAsyncData(
  rfcToBeKey,
  () => api.documentsRetrieve({ draftName: id.value }),
  {
    server: false,
    deep: true // author editing relies on deep reactivity
  }
)

// const { data: capabilities } = await useAsyncData<Capability[]>(
//   'capabilities',
//   () => api.capabilitiesList(),
//   { default: () => ([]), server: false }
// )

const { data: labels } = await useLabels()

const labels1 = computed(() =>
  labels.value.filter((label) => label.used && label.isComplexity && !label.isException)
)

const labels2 = computed(() =>
  labels.value.filter((label) => label.used && label.isComplexity && label.isException)
)

const labels3 = computed(
  () => labels.value.filter((label) => label.used && !label.isComplexity)
)

const selectedLabelIds = ref(rfcToBe.value?.labels ?? [])

watch(
  selectedLabelIds,
  async () => api.documentsPartialUpdate({
    draftName: id.value,
    patchedRfcToBeRequest: {
      labels: selectedLabelIds.value,
    }
  }),
  { deep: true }
)

const {
  data: commentList,
  pending: commentsPending,
  error: commentsError,
  refresh: commentsReload
} = await useCommentsForDraft(id.value)

const { data: relatedDocuments } = await useReferencesForDraft(id.value)

const isAddingToQueue = ref(false)

const snackbar = useSnackbar()

const IN_PROGRESS = 'in_progress'

const addToQueue = async () => {
  isAddingToQueue.value = true
  try {
    const rfcToBe = await api.documentsPartialUpdate({
      draftName: id.value,
      patchedRfcToBeRequest: {
        disposition: IN_PROGRESS
      }
    })
    if(rfcToBe.disposition !== IN_PROGRESS) {
      throw Error(`Unable to set RFC to ${IN_PROGRESS}`)
    }
    await navigateTo(QUEUE_QUEUE_PATH)
  } catch(e) {
    snackbarForErrors({ snackbar, error: e, defaultTitle: 'Unable to add to queue'})
  }
  isAddingToQueue.value = false
}

</script>
