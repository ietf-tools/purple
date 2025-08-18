<template>
  <div>
    <TitleBlock title="Manage Assignments">
      <template #right>
        <RefreshButton :pending="pending" @refresh="refresh"/>
      </template>
    </TitleBlock>

    <div>
      <HeadlessListbox v-model="state.roleFilter" as="div">
        <HeadlessListboxLabel class="block text-sm font-medium leading-6 text-gray-900">Filter</HeadlessListboxLabel>
        <div class="relative mt-2">
          <HeadlessListboxButton
            class="relative cursor-default w-full max-w-md rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
            <span class="block truncate">{{ currentFilterDesc }}</span>
            <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <Icon name="heroicons:chevron-up-down" class="h-5 w-5 text-gray-400" aria-hidden="true"/>
            </span>
          </HeadlessListboxButton>

          <transition
            leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
            leave-to-class="opacity-0">
            <HeadlessListboxOptions
              class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
              <HeadlessListboxOption
                v-slot="{ active, selected }" as="template"
                :value="null">
                <li
                  :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                  <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">Show all documents</span>
                  <span
                    v-if="selected"
                    :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                    <Icon name="heroicons:check" class="h-5 w-5" aria-hidden="true"/>
                  </span>
                </li>
              </HeadlessListboxOption>
              <HeadlessListboxOption
                v-for="role in roles" :key="role.slug" v-slot="{ active, selected }" as="template"
                :value="role.slug">
                <li
                  :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                  <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">Show documents needing {{ role.name }}</span>
                  <span
                    v-if="selected"
                    :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                    <Icon name="heroicons:check" class="h-5 w-5" aria-hidden="true"/>
                  </span>
                </li>
              </HeadlessListboxOption>
            </HeadlessListboxOptions>
          </transition>
        </div>
      </HeadlessListbox>
    </div>
    <div class="mt-8 flow-root">
      <h2 class="text-black dark:text-gray-300 mb-4">Documents for assignment</h2>
      <DocumentCards
        :documents="filteredDocuments"
        :editors="editors?.toSorted(compareEditors)"
        @assign-editor-to-document="(dId: number, edId: number) => saveAssignment({rfcToBe: dId, person: edId})"
        @delete-assignment="deleteAssignment"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ResolvedDocument, ResolvedPerson } from '~/components/AssignmentsTypes'
import type { Assignment, RfcToBe, RpcPerson, RpcRole } from '~/purple_client'
import { DateTime } from 'luxon'

const csrf = useCookie('csrftoken', { sameSite: 'strict' })
const api = useApi()
const snackbar = useSnackbar()

const state = reactive({
  selectedDoc: null,
  roleFilter: null
})

// COMPUTED

const pending = computed(() => pendingPeople?.value || pendingDocs?.value || pendingAssignments?.value)
const cookedAssignments = computed(() => assignments.value?.map(a => ({
  ...a,
  // person is a Person id - replace it with person details
  person: people.value?.find(ed => ed.id === a.person)
})))

const documents = computed(
  () => rfcsToBe.value?.map((rtb) => {
    // Add some fake properties for demonstration purposes
    const assignments = cookedAssignments.value?.filter(a => a.rfcToBe === rtb.id)
    const needsAssignment = rtb.pendingActivities
    const resolvedDocument: ResolvedDocument = { ...rtb, assignments, needsAssignment }
    return resolvedDocument
  })
    .sort(rtb => rtb.externalDeadline ? DateTime.fromJSDate(rtb.externalDeadline).toSeconds() : 0)
)

const filteredDocuments = computed(
  () => documents.value?.filter(
    (rtb: any) => !state.roleFilter || rtb.needsAssignment.some((a) => a.slug === state.roleFilter)
  ) ?? []
)

const editors = computed((): ResolvedPerson[] => {
  const resolvedPeople: ResolvedPerson[] | undefined = people.value?.map(person => ({
    ...person,
    assignments: assignments.value?.filter(a => a.person === person.id)
  }))
  return resolvedPeople || []
})

const currentFilterDesc = computed(() => {
  const currentFilter = roles.value?.find(r => r.slug === state.roleFilter)
  if (currentFilter) {
    return `Show documents needing ${currentFilter.name}`
  }
  return 'Show all documents'
})

// METHODS

async function saveAssignment (assignment: Pick<Assignment, 'rfcToBe' | 'person'>) {
  await $fetch('/api/rpc/assignments/', {
    body: {
      rfc_to_be: assignment.rfcToBe,
      person: assignment.person,
      role: documents.value.find((d: any) => d.id === assignment.rfcToBe)?.needsAssignment?.slug ?? 'first_editor'
    },
    method: 'POST',
    headers: { 'X-CSRFToken': csrf.value?.toString() ?? '' }
  })
  await refresh()
}

// Order editors for display
function compareEditors (a: RpcPerson, b: RpcPerson) {
  const keys: (keyof RpcPerson)[] = ['completeBy', 'name']
  const comparisons = keys.map(attr => {
    const aval = a[attr]
    const bval = b[attr]
    if (typeof aval !== 'number' || typeof bval !== 'number') {
      return 0
    }
    return (aval < bval) ? -1 : ((aval > bval) ? 1 : 0)
  })
  return comparisons.find(c => c !== 0) ?? 0
}

async function deleteAssignment (assignment: Assignment) {
  await $fetch(`/api/rpc/assignments/${assignment.id}/`, {
    method: 'DELETE',
    headers: { 'X-CSRFToken': csrf?.value ?? '' }
  })
  await refresh()
}

async function refresh () {
  const promises = []
  if (refreshPeople) {
    promises.push(refreshPeople())
  }
  if (refreshDocs) {
    promises.push(refreshDocs())
  }
  if (refreshAssignments) {
    promises.push(refreshAssignments())
  }
  await Promise.allSettled(promises)
}

// DATA RETRIEVAL

const { data: people, pending: pendingPeople, refresh: refreshPeople } = await useAsyncData<RpcPerson[]>(
  'rpcPersons',
  () => api.rpcPersonList(),
  { server: false, default: () => ([]) }
)

const { data: rfcsToBe, pending: pendingDocs, refresh: refreshDocs } = await useAsyncData<RfcToBe[]>(
  'rfcsToBe',
  () => api.documentsInProgressList(),
  { server: false, default: () => ([]) }
)
const {
  data: assignments,
  pending: pendingAssignments,
  refresh: refreshAssignments
} = await useAsyncData('assignments', () => api.assignmentsList())

const { data: roles } = await useAsyncData<RpcRole[]>(
  'roles',
  async () => {
    try {
      return (await api.rpcRolesList()).sort((a, b) => a.name.localeCompare(b.name, 'en'))
    } catch (e) {
      snackbar.add({
        type: 'error',
        title: 'Unable to list roles',
        text: e
      })
      return []
    }
  },
  { default: () => ([]) }
)

</script>
