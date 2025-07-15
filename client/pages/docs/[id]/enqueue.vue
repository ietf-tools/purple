<template>
  <div>
    <TitleBlock class="pb-3" :title="`Prep for Queue: ${rfcToBe?.name || '&hellip;'}`"
      summary="Ready the incoming document for the editing queue." />

    <div class="space-y-4">
      <DocInfoCard :draft="rfcToBe" />
      <div class="flex w-full space-x-4">
        <div class="flex flex-col">
          <h2 class="font-bold text-lg border border-gray-200 pl-6 pt-4 pb-2 bg-white rounded-t-xl">Complexities</h2>
          <div class="flex flex-row">
            <DocLabelsCard title="Other complexities" v-model="selectedLabelIds" :labels="labels1" />
            <DocLabelsCard title="Exceptions" v-model="selectedLabelIds" :labels="labels2" />
          </div>
        </div>
        <RpcLabelPicker item-label="slug" v-model="selectedLabelIds" :labels="labels3" />
      </div>
      <DocumentDependencies v-model="relatedDocuments"></DocumentDependencies>
      <BaseCard>
        <template #header>
          <CardHeader title="Comments" />
        </template>
        <div v-if="rfcToBe && rfcToBe.id" class="flex flex-col items-center space-y-4">
          <RpcTextarea v-if="rfcToBe" :draft-name="id" :reload-comments="commentsReload" class="w-4/5 min-w-100" />
          <DocumentComments :draft-name="id" :rfc-to-be-id="rfcToBe.id" :is-loading="commentsPending"
            :error="commentsError" :comment-list="commentList" :reload-comments="commentsReload"
            class="w-3/5 min-w-100" />
        </div>
      </BaseCard>

      <div class="justify-end flex space-x-4">
        <BaseButton btn-type="default">Document has exceptions&mdash;escalate</BaseButton>
        <BaseButton btn-type="default">Add to queue</BaseButton>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { Icon } from '#components'
import { watch } from 'vue'
import type { RfcToBe } from '~/purple_client'

const route = useRoute()
const api = useApi()


const id = computed(() => route.params.id.toString())

const rfcToBeKey = computed(() => `rfcToBe-${id.value}`)

const { data: rfcToBe } = await useAsyncData<RfcToBe>(
  rfcToBeKey,
  () => api.documentsRetrieve({ draftName: route.params.id.toString() }),
  { server: false }
)

// const { data: capabilities } = await useAsyncData<Capability[]>(
//   'capabilities',
//   () => api.capabilitiesList(),
//   { default: () => ([]), server: false }
// )

const { data: labels } = await useAsyncData(
  `labels`,
  () => api.labelsList(),
  {
    default: () => [],
    server: false
  }
)

const labels1 = computed(() =>
  labels.value.filter((label) => label.isComplexity && !label.isException)
)

const labels2 = computed(() =>
  labels.value.filter((label) => label.isComplexity && label.isException)
)

const labels3 = computed(
  () => labels.value.filter((label) => !label.isComplexity)
)

const selectedLabelIds = ref(rfcToBe.value?.labels ?? [])

watch(
  selectedLabelIds,
  async () => api.documentsPartialUpdate({
    draftName: id.value,
    patchedRfcToBe: {
      labels: selectedLabelIds.value,
    }
  }),
  { deep: true }
)

const draftCommentsKey = computed(() => `comments-${id.value}`)

const {
  data: commentList,
  pending: commentsPending,
  error: commentsError,
  refresh: commentsReload
} = await useAsyncData(
  draftCommentsKey,
  () => api.documentsCommentsList({ draftName: id.value })
)

const relatedDocumentsKey = computed(() => `references-${id.value}`)

const { data: relatedDocuments } = await useAsyncData(
  relatedDocumentsKey,
  () => api.documentsReferencesList({
    draftName: id.value
  }),
  {
    default: () => [],
    server: false,
  })

</script>
