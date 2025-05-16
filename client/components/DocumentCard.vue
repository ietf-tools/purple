<!-- Document Card
Based on https://tailwindui.com/components/application-ui/lists/grid-lists#component-2beafc928684743ff886c0b164edb126
-->
<template>
  <li
    :key="cookedDocument.id"
    :class="[props.selected ? 'border-violet-700' : 'border-gray-200', 'rounded-xl border']">
    <div class="flex items-center gap-x-4 border-b border-gray-900/5 bg-gray-50 p-6">
      <Icon
        name="solar:document-text-line-duotone"
        class="h-8 w-8 flex-none"/>
      <div class="text-sm font-medium leading-6 text-gray-900">{{ cookedDocument.name }}</div>
      <BaseBadge v-if="cookedDocument.needsAssignment" :label="`Needs ${cookedDocument.needsAssignment.name}`"/>
      <HeadlessMenu as="div" class="relative ml-auto">
        <HeadlessMenuButton class="-m-2.5 block p-2.5 text-gray-400 hover:text-gray-500">
          <span class="sr-only">Open options</span>
          <Icon name="heroicons:ellipsis-horizontal-20-solid" class="h-5 w-5" aria-hidden="true"/>
        </HeadlessMenuButton>
        <transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100" leave-to-class="transform opacity-0 scale-95">
          <HeadlessMenuItems
            class="absolute right-0 z-10 mt-0.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
            <HeadlessMenuItem v-slot="{ active }">
              <a href="#" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']"
              >View<span class="sr-only">, {{ cookedDocument.name }}</span></a
              >
            </HeadlessMenuItem>
            <HeadlessMenuItem v-slot="{ active }">
              <a href="#" :class="[active ? 'bg-gray-50' : '', 'block px-3 py-1 text-sm leading-6 text-gray-900']">
                Edit<span class="sr-only">, {{ cookedDocument.name }}</span>
              </a>
            </HeadlessMenuItem>
          </HeadlessMenuItems>
        </transition>
      </HeadlessMenu>
    </div>
    <dl class="-my-3 divide-y divide-gray-100 px-6 py-4 text-sm leading-6">
      <div class="flex justify-between gap-x-4 py-3">
        <dt class="text-gray-500">Deadline</dt>
        <dd class="grow flex items-start gap-x-2">
          {{ cookedDocument.externalDeadline?.toLocaleString(DateTime.DATE_FULL) || '-' }}
        </dd>
      </div>
      <div class="flex justify-between gap-x-4 py-3">
        <dt class="text-gray-500">Pages</dt>
        <dd class="grow flex items-start gap-x-2">{{ cookedDocument.pages || '-' }}</dd>
      </div>
      <div class="flex justify-between gap-x-4 py-3">
        <dt class="text-gray-500">Assignments</dt>
        <dd class="">

          {{  cookedDocument.assignmentsPersonIds }}

          <SelectRoot
            :model-value="cookedDocument.assignmentsPersonIds"
            multiple
            @update:model-value="toggleEditor"
          >
            <SelectTrigger
              class="flex flex-row gap-1 items-center relative cursor-pointer rounded-lg bg-white py-2 pl-3 pr-1 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm"
            >
              <div>
                <div
                  v-for="person in uniqBy(cookedDocument.assignmentsPersons, person => person?.id)"
                  :key="person?.id">
                  {{ person.name }}
                </div>
              </div>
              <Icon name="heroicons:chevron-up-down-solid" class="h-5 w-5" aria-hidden="true"/>
            </SelectTrigger>
            <SelectPortal>
              <SelectContent

                position="popper"
        :side-offset="5"
class="overflow-scroll max-h-[40vh]"
              >
                <SelectViewport class="p-[5px] overflow-scroll">
                  <SelectGroup>
                    <SelectItem
                      v-for="editor in cookedDocument.editors"
                      :key="editor.id"
                      :value="editor.id"
                      class="data-[highlighted]:bg-amber-100 data-[highlighted]:text-amber-900 relative cursor-default select-none py-1 pl-1 pr-4"
                    >
                      <SelectItemIndicator>
                        <Icon name="heroicons:check-16-solid" class="h-5 w-5" aria-hidden="true"/>
                      </SelectItemIndicator>
                      {{ editor.name }}
                      <p class="text-gray-500">
                        <template v-if="editor.assignedDocuments">
                          Currently assigned
                          <span v-for="doc in editor.assignedDocuments" :key="doc.id">
                            {{ doc.name }}, {{ doc.pages }} pages
                          </span>
                        </template>
                        <template v-else>
                          Can complete by {{ editor.completeBy.toLocaleString(DateTime.DATE_MED) }}
                        </template>
                      </p>
                  </SelectItem>
                </SelectGroup>
              </SelectViewport>
            </SelectContent>
          </SelectPortal>
          </SelectRoot>
        </dd>
      </div>
    </dl>
  </li>
</template>
<script setup lang="ts">
import { inject } from 'vue'
import { DateTime } from 'luxon'
import { uniqBy } from 'lodash-es'
import { SelectRoot, SelectTrigger, SelectPortal, SelectContent, SelectViewport, SelectGroup, SelectItem, SelectItemIndicator } from 'reka-ui'
import type { AcceptableValue } from 'reka-ui'
import { assignEditorKey, deleteAssignmentKey } from '~/providers/providerKeys'
import type { ResolvedDocument, ResolvedPerson } from './AssignmentsTypes'
import { assert, assertIsArrayOfNumbers, assertIsNumber } from '../utilities/typescript'

type Props = {
  document: ResolvedDocument
  selected?: boolean
  editors?: ResolvedPerson[]
  editorAssignedDocuments?: Record<string, ResolvedDocument[] | undefined>
}

const props = defineProps<Props>()

const currentTime = useCurrentTime()

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

function toggleEditor (editorIds: AcceptableValue) {
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

const cookedDocument = computed(() => {
  const teamPagesPerHour = 1.0
  const assignmentsPersons = props.document?.assignments?.map(
    assignment => props?.editors?.find(editor => editor.id === assignment.person?.id)
  ).filter(editor => !!editor) ?? []
  const assignmentsPersonIds = uniqBy(assignmentsPersons, editor => editor.id)
    .map(editor => editor.id)
    .filter(id => typeof id === 'number')

  const shouldLog = props.document.name === 'draft-ietf-foo-bar'

  return ({
    ...props.document,
    externalDeadline: props.document.externalDeadline && DateTime.fromJSDate(props.document.externalDeadline),
    assignments: props.document.assignments,
    assignmentsPersons,
    assignmentsPersonIds,
    editors: props.editors
      ?.map(editor => {
        const { id, hoursPerWeek } = editor
        assert(typeof id === 'number', 'sdfsdf')
        assertIsNumber(hoursPerWeek)
        const { pages } = props.document
        assertIsNumber(pages)

        const assignedDocuments = props.editorAssignedDocuments?.[id]
        const completeBy = currentTime.value.plus({ days: 7 * pages / teamPagesPerHour / hoursPerWeek })

        if (shouldLog && assignedDocuments && assignmentsPersonIds.includes(id)) {
          console.log(editor.name, editor.id, assignmentsPersonIds)
        }

        return {
          ...editor,
          id,
          assignedDocuments,
          completeBy,
        }
      })
      .sort((a, b) => a.completeBy.toMillis() - b.completeBy.toMillis())
  })
})

</script>
