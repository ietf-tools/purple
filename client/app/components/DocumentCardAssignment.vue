<template>
  <SelectRoot :model-value="cookedDocument.assignmentsPersonIds" multiple @update:model-value="toggleEditor">
    <SelectTrigger
      class="flex flex-row gap-1 items-center relative cursor-pointer rounded-lg bg-white border border-grey-500 dark:bg-black dark:text-white dark:border-gray-500 py-2 pl-3 pr-1 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm">
      <div>
        <div v-if="cookedDocument.assignmentsPersons.length > 0"
          v-for="person in uniqBy(cookedDocument.assignmentsPersons, person => person?.id)" :key="person?.id">
          {{ person.name }}
        </div>
        <div v-else>
          Choose...
        </div>
      </div>
      <Icon name="heroicons:chevron-up-down-solid" class="h-5 w-5" aria-hidden="true" />
    </SelectTrigger>
    <SelectPortal>
      <SelectContent position="popper"
        class="overflow-auto overflow-y-scroll w-full max-w-[800px] max-h-[50vh] bg-white dark:bg-black dark:border-gray-500 border rounded p-1 border-gray-300 shadow-xl">
        <SelectViewport class="p-[5px] overflow-scroll">
          <SelectGroup>
            <SelectItem v-for="editor in cookedDocument.editors" :key="editor.id" :value="editor.id"
              class="cursor-pointer flex data-[highlighted]:bg-amber-100 dark:data-[highlighted]:bg-gray-800 data-[highlighted]:text-amber-900 dark:data-[highlighted]:text-amber-700 relative cursor-default py-1 pl-1 pr-4">
              <div class="shrink-0 grow-0 basis-7">
                <SelectItemIndicator>
                  <Icon name="heroicons:check-16-solid" class="text-black dark:text-purple-300 h-5 w-5"
                    aria-hidden="true" />
                </SelectItemIndicator>
              </div>
              <div>
                <div class="text-gray-500 dark:text-gray-300 font-bold">
                  {{ editor.name }}
                </div>
                <p class="text-gray-500 text-sm">
                  <template v-if="editor.assignedDocuments">
                    Currently assigned
                    <span v-for="doc in editor.assignedDocuments" :key="doc.id">
                      {{ doc.name }}, {{ doc.pages }} pages.
                    </span>
                  </template>
                  <template v-else>
                    Can complete by {{ editor.completeBy.toLocaleString(DateTime.DATE_MED) }}.
                  </template>
                </p>
              </div>
            </SelectItem>
          </SelectGroup>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { uniqBy } from 'lodash-es'
import { SelectRoot, SelectTrigger, SelectPortal, SelectContent, SelectViewport, SelectGroup, SelectItem, SelectItemIndicator } from 'reka-ui'
import type { AcceptableValue } from 'reka-ui'
import { assertIsArrayOfNumbers } from '~/utils/typescript'
import { assignEditorKey, deleteAssignmentKey } from '~/providers/providerKeys'
import type { ResolvedQueueItem } from './AssignmentsTypes'
import type { CookedQueueItem } from '~/utils/rpc'

type Props = {
  document: ResolvedQueueItem
  cookedDocument: CookedQueueItem
}

const props = defineProps<Props>()

function toggleEditor(editorIds: AcceptableValue) {
  assertIsArrayOfNumbers(editorIds)

  const existingAssignmentEditorIds = props.document.assignments?.map(
    assignment => assignment.person?.id
  )

  // Add new editors
  const addEditorIds = editorIds.filter(editorId => !existingAssignmentEditorIds?.includes(editorId))
  addEditorIds.forEach(editorId => assignEditor(props.document.id, editorId))

  // Remove old editors (as assignments)
  const removeEditorIds = existingAssignmentEditorIds?.filter(editorId => typeof editorId === 'number' && !editorIds.includes(editorId))
  const removeAssignments = props.document.assignments?.filter(
    assignment => removeEditorIds?.includes(assignment.person?.id)
  )
  removeAssignments?.forEach(assignment => deleteAssignment(assignment))
}

const _assignEditor = inject(assignEditorKey)
if (!_assignEditor) {
  throw Error('Required assignEditor injection')
}
const assignEditor = _assignEditor

const _deleteAssignment = inject(deleteAssignmentKey)
if (!_deleteAssignment) {
  throw Error('Required deleteAssignment injection')
}
const deleteAssignment = _deleteAssignment

</script>
