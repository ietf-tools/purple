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

const relatedDocuments = defineModel<RpcRelatedDocument[]>({ default: [] })

const columns: Column[] = [
  {
    key: 'name',
    label: 'Document',
    field: 'id' satisfies keyof RpcRelatedDocument,
    classes: 'text-sm font-medium'
  },
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
  }
]

const isOpenDependencyModal = ref(false)

type Props = {
  draftName: string
  id: number,
}

const props = defineProps<Props>()

</script>
