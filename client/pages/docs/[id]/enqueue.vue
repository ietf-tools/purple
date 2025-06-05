<template>
  <div>
    <TitleBlock
      class="pb-3"
      :title="`Prep for Queue: ${rfcToBe?.name || '&hellip;'}`"
      summary="Ready the incoming document for the editing queue."/>

    <div class="space-y-4">
      <DocInfoCard :draft="rfcToBe"/>
      <div class="flex space-x-4">
        <DocComplexityCard :capabilities="capabilities"/>
        <DocExceptionsCard :labels="labels"/>
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
          row-key="name"/>
      </BaseCard>
      <BaseCard>
        <template #header>
          <CardHeader title="Comments"/>
        </template>
        <div class="flex flex-col items-center space-y-4">
          <RpcTextarea class="w-4/5 min-w-100"/>
          <HistoryFeed class="w-3/5 min-w-100"/>
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

import type { Capability, Label, RfcToBe } from '~/purple_client'
import type { Column } from '~/components/DocumentTableTypes'

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
  },
]

const relatedDocuments = [
  {
    name: 'draft-some-other-draft',
    relationship: 'Normative Reference',
    currentState: 'Active WG document'
  },
]

const { data: rfcToBe } = await useAsyncData<RfcToBe>(
  computed(() => `rfcToBe-${route.params.id}`),
  () => api.documentsRetrieve({ draftName: route.params.id.toString() }),
  { server: false }
)

const { data: capabilities } = await useAsyncData<Capability[]>(
  'capabilities',
  () => api.capabilitiesList(),
  { default: () => ([]), server: false }
)

const { data: labels } = await useAsyncData<Label[]>(
  'labels',
  () => api.labelsList(),
  { default: () => ([]), server: false }
)
</script>
