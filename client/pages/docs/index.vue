<template>
  <div>
    <TitleBlock title="My Documents" summary="Documents assigned to me">
      <template #right>
        <RefreshButton class="mr-3"/>
        <NuxtLink
          v-if="userStore.isManager"
          class="max-w-l items-center rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          to="/docs/assignments">
          Manage Assignments
        </NuxtLink>
      </template>
    </TitleBlock>
    <div class="mt-8 flow-root">
      <DocumentTable
        :columns="columns"
        :data="myAssignments.map(a => ({ ...a.rfcToBe })).filter(row => !!row)"
        row-key="id"
        :loading="pending"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAsyncData } from '#app'
import type { Column } from '~/components/DocumentTableTypes'

const api = useApi()
const userStore = useUserStore()

// DATA

const columns: Column[] = [
  {
    key: 'name',
    label: 'Document',
    field: 'name',
    classes: 'text-sm font-medium',
    link: row => `/docs/${row.name}`
  },
  {
    field: 'labels',
    key: 'labels',
    label: 'Labels',
    labels: row => {
      // @ts-ignore
      return row.labels.map(lblId => labels.value.find(lbl => lbl.id === lblId)) || []
    }
  }
]

const { data: myAssignments } = await useAsyncData(
  'myAssignments',
  () => api.assignmentsList(),
  { server: false, default: () => ([]) }
)

const { data: labels } = await useAsyncData(
  'labels',
  () => api.labelsList(),
  { server: false, default: () => ([]) }
)

</script>
