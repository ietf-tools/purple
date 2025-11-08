<!-- Document Cards
Based on https://tailwindui.com/components/application-ui/lists/grid-lists#component-2beafc928684743ff886c0b164edb126
-->
<template>
  <ul role="list" class="grid grid-cols-1 gap-x-6 gap-y-8 lg:grid-cols-3 xl:gap-x-8">
    <DocumentCard
      v-for="doc of props.documents"
      :key="doc.id"
      :document="doc"
      :editors="props.editors"
      :selected="state.selectedDoc?.id === doc.id"
      :editor-assigned-documents="editorAssignedDocuments"
    />
  </ul>
</template>

<script setup lang="ts">
import { provide } from 'vue'
import { assignEditorKey, deleteAssignmentKey } from '~/providers/providerKeys'
import type { ResolvedQueueItem, ResolvedPerson } from './AssignmentsTypes'

type Props = {
  documents: ResolvedQueueItem[]
  editors: ResolvedPerson[]
}

const props = defineProps<Props>()

const state = reactive<{ selectedDoc: null | ResolvedQueueItem }>({
  selectedDoc: null
})

const emit = defineEmits(['assignEditorToDocument', 'deleteAssignment'])

provide(assignEditorKey, (doc, editor) => emit('assignEditorToDocument', doc, editor))
provide(deleteAssignmentKey, (assignment) => emit('deleteAssignment', assignment))

const editorAssignedDocuments = computed(() =>
  props.documents.reduce((editorAssignedDocuments, resolvedDocument) => {
    resolvedDocument.assignments?.forEach(assignment => {
      const editorId = assignment.person?.id
      if (editorId && !editorAssignedDocuments[editorId]) {
        editorAssignedDocuments[editorId] = []
      }
      if (editorId &&
      Array.isArray(editorAssignedDocuments[editorId]) &&
      !editorAssignedDocuments[editorId]?.find(
        existingDocument => existingDocument.id === resolvedDocument.id
      )) {
        editorAssignedDocuments[editorId].push(resolvedDocument)
      }
    })
    return editorAssignedDocuments
  }, {} as Record<string, ResolvedQueueItem[] | undefined>)
)

</script>
