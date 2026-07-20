<template>
  <div>
    <header class="relative isolate">
      <div class="absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
        <div
          class="absolute left-16 top-full -mt-16 transform-gpu opacity-50 blur-3xl xl:left-1/2 xl:-ml-80">
          <div
            class="aspect-[1154/678] w-[72.125rem] bg-gradient-to-br from-[#FF80B5] to-[#9089FC]"
            style="
              clip-path: polygon(
                100% 38.5%,
                82.6% 100%,
                60.2% 37.7%,
                52.4% 32.1%,
                47.5% 41.8%,
                45.2% 65.6%,
                27.5% 23.4%,
                0.1% 35.3%,
                17.9% 0%,
                27.7% 23.4%,
                76.2% 2.5%,
                74.2% 56%,
                100% 38.5%
              );
            " />
        </div>
        <div class="absolute inset-x-0 bottom-0 h-px bg-gray-900/5" />
      </div>

      <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div
          class="mx-auto flex max-w-2xl items-center justify-between gap-x-8 lg:mx-0 lg:max-w-none">
          <div class="flex items-center gap-x-6">
            <img
              :src="person?.picture || `https://i.pravatar.cc/150?img=${route.params.id}`"
              :alt="person?.name || 'Person'"
              class="w-16 flex-none rounded-full ring-1 ring-gray-900/10" />
            <h1>
              <span class="mt-1 text-xl font-semibold leading-6 text-gray-900 dark:text-white">
                {{ person?.name || 'Loading...' }}
              </span>
              <br />
              <span class="text-sm leading-6 text-gray-500 dark:text-neutral-400">
                {{ person?.email || '' }}
              </span>
            </h1>
          </div>
          <HeadlessMenu as="div" class="relative sm:hidden">
            <HeadlessMenuButton class="-m-3 block p-3">
              <span class="sr-only">More</span>
              <Icon name="uil:bars" class="h-5 w-5 text-gray-500" aria-hidden="true" />
            </HeadlessMenuButton>

            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95">
              <HeadlessMenuItems
                class="absolute right-0 z-10 mt-0.5 w-32 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-900/5 focus:outline-none">
                <HeadlessMenuItem v-slot="{ active }">
                  <button
                    type="button"
                    :class="[
                      active ? 'bg-gray-50' : '',
                      'block w-full px-3 py-1 text-left text-sm leading-6 text-gray-900'
                    ]">
                    Copy URL
                  </button>
                </HeadlessMenuItem>
                <HeadlessMenuItem v-slot="{ active }">
                  <a
                    href="#"
                    :class="[
                      active ? 'bg-gray-50' : '',
                      'block px-3 py-1 text-sm leading-6 text-gray-900'
                    ]"
                    >Edit</a
                  >
                </HeadlessMenuItem>
              </HeadlessMenuItems>
            </transition>
          </HeadlessMenu>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <!-- Summary bar -->
      <div class="mb-6 rounded-lg bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5">
        <dl class="flex flex-wrap divide-x divide-gray-900/5 dark:divide-white/10">
          <div class="px-6 py-4">
            <dt class="text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-200">
              Workload
            </dt>
            <dd class="mt-1 text-sm leading-6 text-gray-900 dark:text-neutral-300">
              <WorkloadSummary v-if="personWorkload" :workload="personWorkload" mode="rows" />
              <Icon v-else name="ei:spinner-3" size="0.8em" class="animate-spin" />
            </dd>
          </div>
          <div class="px-6 py-4">
            <dt class="text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-200">
              Status
            </dt>
            <dd class="mt-1" v-if="person">
              <span
                :class="[
                  person?.isActive === true
                    ? 'bg-green-50 text-green-600 ring-green-600/20'
                    : 'bg-red-50 text-red-600 ring-red-600/20',
                  'rounded-md px-2 py-1 text-xs ring-1 ring-inset'
                ]">
                <template v-if="person.isActive">active</template>
                <template v-else>inactive</template>
              </span>
            </dd>
          </div>
          <div class="px-6 py-4">
            <dt class="text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-200">
              Roles
            </dt>
            <dd class="mt-1 text-sm leading-6 text-gray-600 dark:text-neutral-400">
              <template v-if="personStatus === 'pending'">
                <Icon name="ei:spinner-3" size="0.8em" class="animate-spin" />
              </template>
              <template v-if="personStatus === 'success'">
                {{
                  person?.roles && person.roles.length > 0
                    ? person.roles.map((role) => role.name).join(', ')
                    : 'No roles assigned'
                }}
              </template>
            </dd>
          </div>
        </dl>
      </div>

      <!-- Assignments List -->
      <div>
        <div class="rounded-lg bg-white dark:bg-neutral-900 shadow-sm ring-1 ring-gray-900/5 p-6">
          <h2 class="text-sm font-semibold leading-6 text-gray-900 dark:text-neutral-200">
            Active Assignments
          </h2>

          <template v-if="assignmentsStatus === 'error'">
            {{ assignmentsError }}
            (note: this might be a permissions error)
          </template>

          <template v-if="assignmentsStatus === 'pending'">
            <Icon name="ei:spinner-3" size="1em" class="animate-spin" />
          </template>

          <template v-if="assignmentsStatus === 'success'">
            <div v-if="sortedAssignments.length > 0" class="mt-4">
              <RpcTable>
                <RpcThead>
                  <tr
                    v-for="headerGroup in assignmentsTable.getHeaderGroups()"
                    :key="headerGroup.id">
                    <RpcTh
                      v-for="header in headerGroup.headers"
                      :key="header.id"
                      :colSpan="header.colSpan"
                      :is-sortable="header.column.getCanSort()"
                      :sort-direction="header.column.getIsSorted()"
                      :column-name="getVNodeText(header.column.columnDef.header)"
                      @click="header.column.getToggleSortingHandler()?.($event)">
                      <div class="flex items-center gap-2">
                        <FlexRender
                          v-if="!header.isPlaceholder"
                          :render="header.column.columnDef.header"
                          :props="header.getContext()" />
                      </div>
                    </RpcTh>
                  </tr>
                </RpcThead>
                <RpcTbody>
                  <tr v-for="row in assignmentsTable.getRowModel().rows" :key="row.id">
                    <RpcTd v-for="cell in row.getVisibleCells()" :key="cell.id">
                      <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
                    </RpcTd>
                  </tr>
                </RpcTbody>
              </RpcTable>
            </div>
            <div v-else class="mt-6 text-center py-8">
              <p class="text-sm text-gray-500">No current assignments</p>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Anchor, Icon, RpcLabel } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  getSortedRowModel,
  useVueTable,
  createColumnHelper
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'
import { useLocalStorage } from '@vueuse/core'
import { DateTime } from 'luxon'
import type { Cluster, Label, NestedAssignment } from '~/purple_client'
import { calculateEnqueuedAtData, renderEnqueuedAt } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'

const route = useRoute()
const api = useApi()

const personId = computed(() => {
  const id = route.params.id
  if (!id) {
    throw Error(`Expected id but was ${id} (typeof ${typeof id})`)
  }
  return parseInt(id.toString(), 10)
})

console.log({ personId: personId.value })

// Fetch person data
const {
  data: person,
  status: personStatus,
  error: personError
} = await useAsyncData(
  `person-${route.params.id}`,
  () => api.rpcPersonRetrieve({ id: personId.value }),
  { server: false, lazy: true }
)

// Fetch person assignments
const {
  data: assignments,
  status: assignmentsStatus,
  error: assignmentsError
} = await useAsyncData(
  `person-assignments-${route.params.id}`,
  () => api.rpcPersonAssignmentsList({ personId: personId.value }),
  { server: false, lazy: true }
)

const {
  data: clusters,
  status: clustersStatus,
  error: clustersError
} = await useAsyncData(() => api.clustersList(), {
  server: false,
  lazy: true,
  default: () => [] as Cluster[]
})

const { data: allLabels } = await useAsyncData('labels', () => api.labelsList(), {
  server: false,
  lazy: true,
  default: () => [] as Label[]
})

const ROLES = [
  { slug: 'enqueuer', label: 'Enqueuer' },
  { slug: 'ref_checker', label: 'Ref Checker' },
  { slug: 'formatting', label: 'Formatting' },
  { slug: 'first_editor', label: 'First Edit' },
  { slug: 'second_editor', label: 'Second Edit' },
  { slug: 'final_review_editor', label: 'Final Review' },
  { slug: 'publisher', label: 'Publisher' }
]

const roleLabel = (slug: string) => ROLES.find((r) => r.slug === slug)?.label ?? slug
const roleOrder = (slug: string) => ROLES.findIndex((r) => r.slug === slug)

// For a blocked assignment, find its current workflow stage from the document's
// pending activities
const blockedStage = (a: NestedAssignment): { slug: string; index: number } | null =>
  (a.rfcToBe?.pendingActivities ?? []).reduce<{ slug: string; index: number } | null>(
    (best, activity) => {
      const index = roleOrder(activity.slug)
      if (index === -1) return best
      return best === null || index < best.index ? { slug: activity.slug, index } : best
    },
    null
  )

const sortedAssignments = computed(() => {
  if (!assignments.value) return []

  const order = (a: (typeof assignments.value)[number]): number => {
    if (a.role === 'blocked') {
      // Sort immediately after the inferred stage, or to the very end if unknown.
      const stage = blockedStage(a)
      return stage ? stage.index + 0.5 : ROLES.length + 1
    }
    const idx = roleOrder(a.role)
    return idx === -1 ? ROLES.length : idx
  }

  return [...assignments.value].sort((a, b) => {
    const roleDiff = order(a) - order(b)
    if (roleDiff !== 0) return roleDiff
    // Within the same role, newest enqueue date first
    const aTime = a.enqueuedAt?.getTime() ?? -Infinity
    const bTime = b.enqueuedAt?.getTime() ?? -Infinity
    return bTime - aTime
  })
})

const assignmentColumnHelper = createColumnHelper<NestedAssignment>()
const assignmentSorting = useLocalStorage<SortingState>('team-member-assignments-sorting', [])

const assignmentDisplayRole = (a: NestedAssignment): string => {
  if (a.role !== 'blocked') return a.role
  return blockedStage(a)?.slug ?? 'blocked'
}

const assignmentColumns = [
  assignmentColumnHelper.accessor((a) => a.rfcToBe?.rfcNumber ?? null, {
    id: 'rfcNumber',
    header: 'RFC',
    cell: (data) => {
      const num = data.getValue()
      return num ? h('span', { class: 'font-mono' }, `RFC ${num}`) : ''
    },
    sortingFn: 'alphanumeric',
    sortUndefined: 'last'
  }),
  assignmentColumnHelper.display({
    id: 'document',
    header: 'Document',
    cell: ({ row }) => {
      const a = row.original
      const name = a.rfcToBe?.draft?.name ?? ''
      const linkNode = h(Anchor, { href: `/docs/${name}`, class: ANCHOR_STYLE }, () => name)
      const blockingReasons = a.role === 'blocked' ? (a.rfcToBe?.blockingReasons ?? []) : []
      return h('div', [
        linkNode,
        blockingReasons.length
          ? h(
              'ul',
              { class: 'mt-0.5 list-disc list-inside text-xs text-red-500 dark:text-red-400' },
              blockingReasons.map((br) => h('li', br.reason?.name))
            )
          : null,
        a.comment
          ? h(
              'blockquote',
              {
                class:
                  'mt-1 border-l-2 border-gray-300 dark:border-neutral-600 pl-2 text-xs italic text-gray-500 dark:text-neutral-400'
              },
              a.comment
            )
          : null
      ])
    },
    enableSorting: false
  }),
  assignmentColumnHelper.display({
    id: 'labels',
    header: 'Labels',
    cell: ({ row }) => {
      const ids = row.original.rfcToBe?.labels ?? []
      if (!ids.length) return ''
      const resolved = ids
        .map((id) => allLabels.value.find((l) => l.id === id))
        .filter(Boolean) as Label[]
      if (!resolved.length) return ''
      return h(
        'span',
        { class: 'flex flex-wrap gap-1' },
        resolved.map((l) => h(RpcLabel, { label: l }))
      )
    },
    enableSorting: false
  }),
  assignmentColumnHelper.accessor('role', {
    header: 'Role',
    cell: ({ row }) => {
      const a = row.original
      const displayRole = assignmentDisplayRole(a)
      const label = roleLabel(displayRole)
      const isBlocked = a.role === 'blocked'
      return h(
        'span',
        { class: isBlocked ? 'text-red-600 dark:text-red-400' : '' },
        isBlocked ? `${label} (blocked)` : label
      )
    },
    sortingFn: (rowA, rowB) => {
      const orderA = roleOrder(assignmentDisplayRole(rowA.original))
      const orderB = roleOrder(assignmentDisplayRole(rowB.original))
      return orderA - orderB
    }
  }),
  assignmentColumnHelper.accessor('enqueuedAt', {
    header: () =>
      h('div', { class: 'text-center' }, [
        h('div', 'Enqueue Date'),
        h('div', { class: 'text-xs' }, '(Weeks in queue)')
      ]),
    cell: (data) => {
      const value = data.getValue()
      if (!value) return ''
      return renderEnqueuedAt(calculateEnqueuedAtData(value))
    },
    sortingFn: (rowA, rowB, columnId) => {
      const a = rowA.getValue<Date | null | undefined>(columnId)
      const b = rowB.getValue<Date | null | undefined>(columnId)
      const aTime = a instanceof Date ? a.getTime() : -Infinity
      const bTime = b instanceof Date ? b.getTime() : -Infinity
      return aTime - bTime
    }
  }),
  assignmentColumnHelper.accessor('assignedAt', {
    header: 'Assigned Date',
    cell: (data) => {
      const value = data.getValue()
      if (!value) return ''
      return h(
        'time',
        { datetime: value.toISOString(), class: 'text-xs' },
        DateTime.fromJSDate(value).toISODate() ?? ''
      )
    },
    sortingFn: (rowA, rowB, columnId) => {
      const a = rowA.getValue<Date | null | undefined>(columnId)
      const b = rowB.getValue<Date | null | undefined>(columnId)
      const aTime = a instanceof Date ? a.getTime() : -Infinity
      const bTime = b instanceof Date ? b.getTime() : -Infinity
      return aTime - bTime
    },
    sortUndefined: 'last'
  }),
  assignmentColumnHelper.accessor('state', {
    header: 'Status',
    cell: (data) => {
      const v = data.getValue()
      if (!v) return ''
      const cls =
        v === 'done' ? 'text-green-600' : v === 'in_progress' ? 'text-blue-600' : 'text-yellow-600'
      return h('span', { class: cls }, v)
    },
    sortingFn: 'alphanumeric'
  }),
  assignmentColumnHelper.accessor((a) => a.rfcToBe?.cluster?.number ?? null, {
    id: 'cluster',
    header: 'Cluster',
    cell: ({ row }) => {
      const num = row.original.rfcToBe?.cluster?.number
      if (!num) return ''
      return h(Anchor, { href: `/clusters/${num}`, class: ANCHOR_STYLE }, () => [
        h(Icon, { name: 'pajamas:group', class: 'h-4 w-4 inline-block mr-1' }),
        String(num)
      ])
    },
    sortingFn: 'alphanumeric',
    sortUndefined: 'last'
  }),
  assignmentColumnHelper.accessor((a) => a.rfcToBe?.draft?.pages ?? null, {
    id: 'pages',
    header: 'Pages',
    cell: (data) => data.getValue() ?? '-',
    sortingFn: 'alphanumeric',
    sortUndefined: 'last'
  })
]

const assignmentsTable = useVueTable({
  get data() {
    return sortedAssignments.value
  },
  columns: assignmentColumns,
  state: {
    get sorting() {
      return assignmentSorting.value
    }
  },
  onSortingChange: (updater) => {
    assignmentSorting.value =
      typeof updater === 'function' ? updater(assignmentSorting.value) : updater
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  manualSorting: false
})

// Handle error state
if (personError.value) {
  throw createError({
    statusCode: 404,
    statusMessage: `Error fetching person: ${personError.value}`
  })
}

const personWorkload = computed((): RpcPeopleWorkload[number] | undefined => {
  if (!person.value || !assignments.value) return undefined
  const { id: personId } = person.value
  if (personId === undefined) return undefined
  const docs = assignments.value
    .map((assignment) => {
      const pages = assignment.rfcToBe?.draft?.pages ?? 0
      return { ...assignment.rfcToBe, pages }
    })
    .filter((maybeDoc) => !!maybeDoc)
  return calculatePeopleWorkload(clusters.value, docs)[personId]
})

useHead(() => ({
  title: person.value ? person.value.name : 'Loading...'
}))
</script>
