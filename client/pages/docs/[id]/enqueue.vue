<template>
  <div>
    <TitleBlock
      class="pb-3"
      :title="`Prep for Queue: ${rfcToBe?.name || '&hellip;'}`"
      summary="Ready the incoming document for the editing queue."
    />

    <div class="space-y-4">
      <DocInfoCard :draft="rfcToBe" />
      <div class="flex w-full space-x-4">
        <DocLabelsCard
          title="Complexities"
          v-model="selectedLabelIds"
          :labels="labels1"
        />
        <DocLabelsCard
          title="Exceptions"
          v-model="selectedLabelIds"
          :labels="labels2"
        />
        <RpcLabelPicker
          item-label="slug"
          v-model="selectedLabelIds"
          :labels="labels3"
        />
      </div>
      <BaseCard>
        <template #header>
          <CardHeader title="Document Dependencies">
            <template #actions>
              <BaseButton btn-type="default">Add Dependency</BaseButton>
            </template>
          </CardHeader>
        </template>
        <DocumentTable
          :columns="columns"
          :data="relatedDocuments"
          row-key="name"
        />
      </BaseCard>
      <BaseCard>
        <template #header>
          <CardHeader title="Comments" />
        </template>
        <div
          v-if="rfcToBe && rfcToBe.id"
          class="flex flex-col items-center space-y-4"
        >
          <RpcTextarea
            v-if="rfcToBe"
            :draft-name="id"
            :reload-comments="commentsReload"
            class="w-4/5 min-w-100"
          />
          <DocumentComments
            v-if="rfcToBe"
            :draft-name="id"
            :rfc-to-be-id="rfcToBe.id"
            :is-loading="commentsPending"
            :error="commentsError"
            :comment-list="commentList"
            :reload-comments="commentsReload"
            class="w-3/5 min-w-100"
          />
        </div>
      </BaseCard>

      <div class="justify-end flex space-x-4">
        <BaseButton btn-type="default"
          >Document has exceptions&mdash;escalate</BaseButton
        >
        <BaseButton btn-type="default">Add to queue</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import type { Column } from '~/components/DocumentTableTypes'
import type { RfcToBe } from '~/purple_client'

const route = useRoute()
const api = useApi()

const columns: Column[] = [
  {
    key: 'name',
    label: 'Document',
    field: 'name',
    classes: 'text-sm font-medium'
  },
  {
    key: 'relationship',
    label: 'Relationship',
    field: 'relationship',
    classes: 'text-sm font-medium'
  },
  {
    key: 'currentState',
    label: 'Current State',
    field: 'currentState',
    classes: 'text-sm font-medium'
  }
]

const relatedDocuments = [
  {
    name: 'draft-some-other-draft',
    relationship: 'Normative Reference',
    currentState: 'Active WG document'
  }
]

const id = computed(() => route.params.id.toString())

const { data: rfcToBe } = await useAsyncData<RfcToBe>(
  computed(() => `rfcToBe-${id.value}`),
  () => api.documentsRetrieve({ draftName: route.params.id.toString() }),
  { server: false }
)

// const { data: capabilities } = await useAsyncData<Capability[]>(
//   'capabilities',
//   () => api.capabilitiesList(),
//   { default: () => ([]), server: false }
// )

const { data: labels } = await useAsyncData('labels', () => api.labelsList(), {
  default: () => [],
  server: false
})

const labels1 = computed(() =>
  labels.value.filter((label) => label.isComplexity && !label.isException)
)

const labels2 = computed(() =>
  labels.value.filter((label) => label.isComplexity && label.isException)
)

const labels3 = computed(
  () => labels.value.filter((label) => !label.isComplexity)
)

const { data: defaultSelectedLabelIds } = await useAsyncData<number[]>(
  () => `user-selection-${id.value}`,
  async () => {
    return [] // FIXME: get user values
  }
)

const selectedLabelIds = ref(defaultSelectedLabelIds.value ?? [])

watch(
  selectedLabelIds,
  async () => {
    console.log('CHANGE TO SEND TO API', {
      ids: selectedLabelIds.value ? Array.from(selectedLabelIds.value) : []
    })
  },
  { deep: true }
)

const key = computed(() => `comments-${id.value}`)

const {
  data: commentList,
  pending: commentsPending,
  error: commentsError,
  refresh: commentsReload
} = useAsyncData(key, () =>
  api.documentsCommentsList({ draftName: id.value })
)

</script>
