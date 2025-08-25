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
import type { RpcRelatedDocument } from '~/purple_client';
import type { Column } from './DocumentTableTypes';
import { h } from 'vue'
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
    key: 'currentState',
    label: 'Current State',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium'
  },
  {
    key: 'currentAssignments',
    label: 'Current Assignments',
    field: 'targetDraftName' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium',
    format: (row: any) => {
      const info = props.relatedDocsInfo?.[row] || {}
      const assignments = info.assignment_set
      if (!assignments || !Array.isArray(assignments) || assignments.length === 0) return '—'
      const nodes = []
      assignments.forEach((assignment: any, idx: number) => {
        const person = (props.people || []).find((p: any) => p.id === assignment.person)
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
      const info = props.relatedDocsInfo?.[row] || {}
      const pending = info.pending_activities
      if (!pending || !Array.isArray(pending) || pending.length === 0) return '—'
      const nodes = []
      pending.forEach((a: any, idx: number) => {
        nodes.push(h(BaseBadge, { label: a.name }))
        if (idx < pending.length - 1) nodes.push(', ')
      })
      return nodes
    }
  }
]

const isOpenDependencyModal = ref(false)

type Props = {
  draftName: string
  id: number,
  relatedDocsInfo: Record<string, { assignment_set?: any; pending_activities?: any }>
  people: any[]
}

const props = defineProps<Props>()

</script>
