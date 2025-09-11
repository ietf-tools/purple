<template>
  <div>
    <BaseCard>
      <template #header>
        <CardHeader title="Document Dependencies">
          <template #actions>
            <BaseButton btn-type="default" @click="isOpenDependencyModal = true">Add Dependency</BaseButton>
          </template>
        </CardHeader>
      </template>
      <div class="flex items-center gap-2 mb-4">
        <span class="font-medium">Cluster: </span>
        <span class="mr-2">
          <span v-if="props.clusterNumber">
            <Anchor :href="`/clusters/${props.clusterNumber}`" class="inline-flex items-center gap-1 text-blue-600">
              <Icon name="pajamas:group" class="h-5 w-5" />{{ props.clusterNumber }}
            </Anchor>
          </span>
        <span v-else>-</span>
        </span>
      </div>
      <DocumentTable v-if="relatedDocuments" :columns="columns" :data="relatedDocuments" row-key="id" />
    </BaseCard>
    <DocumentDependenciesAdd
      v-model:is-open-dependency-modal="isOpenDependencyModal"
      v-model:related-documents="relatedDocuments"
      :draft-name="props.draftName"
      :id="props.id"
    />
</div>
</template>

<script setup lang="ts">
import type { RpcRelatedDocument, RpcPerson } from '~~/purple_client';
import type { Column } from './DocumentTableTypes';
import { h } from 'vue'
import { Anchor } from '#components'
import BaseBadge from './BaseBadge.vue'

const relatedDocuments = defineModel<RpcRelatedDocument[]>({ default: [] })

const columns: Column[] = [
  {
    key: 'relationship',
    label: 'Relationship',
    field: 'relationship' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium'
  },
  {
    key: 'targetDraftName',
    label: 'Target Draft Name',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
      return h(Anchor, {
        href: `/docs/${row}`,
        class: 'inline-flex items-center gap-1 text-blue-600'
      }, row)
    }
  },
  {
    key: 'pendingActivities',
    label: 'Current Assignments',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
      const info = relatedDocsInfo.value?.[row] || {}
      const assignments = info.assignment_set
      if (!assignments || !Array.isArray(assignments) || assignments.length === 0) return '—'
      const nodes: (string | VNode)[] = []
      assignments.forEach((assignment: any, idx: number) => {
        const person = (people.value || []).find((p: any) => p.id === assignment.person)
        nodes.push(
          h('span', [
            h(BaseBadge, { label: assignment.role }),
            ' ',
            person ? `(${person.name})` : ''
          ])
        )
        if (idx < assignments.length - 1) nodes.push(', ')
      })
      return nodes
    }
  },
  {
    key: 'pendingActivities',
    label: 'Pending Activities',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
    const info = relatedDocsInfo.value?.[row] || {}
      const pending = info.pending_activities
      if (!pending || !Array.isArray(pending) || pending.length === 0) return '—'
      const nodes: (string | VNode)[] = []
      pending.forEach((a: any, idx: number) => {
        nodes.push(h(BaseBadge, { label: a.name }))
        if (idx < pending.length - 1) nodes.push(', ')
      })
      return nodes
    }
  },
  {
    key: 'notReceivedCount',
    label: 'not received #',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
      const info = relatedDocsInfo.value?.[row] || {}
      return info.not_received_count || 0
    }
  },
    {
    key: 'refqueueCount',
    label: 'refqueue #',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
      const info = relatedDocsInfo.value?.[row] || {}
      return info.refqueue_count || 0
    }
  }
]

const isOpenDependencyModal = ref(false)

type Props = {
  draftName: string
  id: number,
  people?: RpcPerson[],
  clusterNumber?: number
}

const api = useApi()
const props = defineProps<Props>()

const people = ref<RpcPerson[]>(props.people ?? [])

if (!props.people) {
  const { data: fetchedPeople } = await useAsyncData(
    () => api.rpcPersonList(),
    { server: false, default: () => [] }
  )
  if (fetchedPeople.value) people.value = fetchedPeople.value
}

// Fetch additional info for each related document
const relatedDocsInfo = ref<Record<string, any>>({})
watch(
  () => relatedDocuments.value,
  async (docs) => {
    if (!docs) return
    const names = docs
      .filter(doc => doc.relationship !== 'not-received')
      .map(doc => doc.targetDraftName)
      .filter(Boolean)
    const uniqueNames = Array.from(new Set(names))
    for (const name of uniqueNames) {
      if (!name || relatedDocsInfo.value[name]) continue
      try {
        const [info, relDocs] = await Promise.all([
          api.documentsRetrieve({ draftName: name }),
          api.documentsReferencesList({ draftName: name })
        ])
        const refqueueCount = relDocs.filter(doc => doc.relationship === 'refqueue').length
        const notReceivedCount = relDocs.filter(doc => doc.relationship === 'not-received').length
        relatedDocsInfo.value[name] = {
          assignment_set: info.assignmentSet,
          pending_activities: info.pendingActivities,
          refqueue_count: refqueueCount,
          not_received_count: notReceivedCount
        }
      } catch (e) {
        relatedDocsInfo.value[name] = undefined
      }
    }
  },
  { immediate: true }
)

</script>
