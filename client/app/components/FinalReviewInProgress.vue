<template>
  <div>
    <Heading :heading-level="props.headingLevel" class="mt-5">
      In Progress {{ status === 'success' ? `(${table.getRowCount()})` : '' }}
    </Heading>
    <ErrorAlert v-if="error">
      {{ error }}
    </ErrorAlert>
    <RpcTable>
      <RpcThead>
        <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
            :is-sortable="header.column.getCanSort()" :sort-direction="header.column.getIsSorted()"
            @click="header.column.getToggleSortingHandler()?.($event)">
            <div class="flex items-center gap-2">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
              <Transition name="sort-indicator">
                <Icon v-if="header.column.getCanSort()" name="heroicons:arrows-up-down"
                  class="text-gray-400 opacity-60 hover:opacity-100" />
              </Transition>
            </div>
          </RpcTh>
        </tr>
      </RpcThead>
      <RpcTbody>
        <RpcRowMessage :status="status" :column-count="table.getAllColumns().length"
          :row-count="table.getRowModel().rows.length" />
        <tr v-for="row in table.getRowModel().rows" :key="row.id">
          <RpcTd v-for="cell in row.getVisibleCells()" :key="cell.id">
            <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
          </RpcTd>
        </tr>
      </RpcTbody>
      <RpcTfoot>
        <tr v-for="footerGroup in table.getFooterGroups()" :key="footerGroup.id">
          <RpcTh v-for="header in footerGroup.headers" :key="header.id" :colSpan="header.colSpan">
            <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.footer"
              :props="header.getContext()" />
          </RpcTh>
        </tr>
      </RpcTfoot>
    </RpcTable>
  </div>
</template>

<script setup lang="ts">
import { Anchor, BaseBadge, Icon } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
  type SortingState,
} from '@tanstack/vue-table'
import type { QueueItem } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import type { HeadingLevel } from '~/utils/html'
import { groupBy, uniqBy } from 'lodash-es'

type Props = {
  name?: string
  headingLevel?: HeadingLevel
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 2 })

const api = useApi()

const {
  data: queueItems,
  pending,
  status,
  refresh,
  error,
} = await useAsyncData(
  'final-review-in-progress',
  () => api.queueList({ pendingFinalApproval: true }),
  {
    server: false,
    lazy: true,
    default: () => [] as QueueItem[],
  }
)

const columnHelper = createColumnHelper<QueueItem>()

const columns = [
  columnHelper.display({
    id: 'icon',
    header: '',
    cell: () => h(Icon, { name: "uil:file-alt", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" })
  }),
  columnHelper.accessor('name', {
    header: 'Document',
    cell: data => {
      return h(Anchor, { href: documentPathBuilder(data.row.original), 'class': ANCHOR_STYLE }, () => [
        data.getValue(),
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('rfcNumber', {
    header: 'RFC Number',
    cell: data => data.getValue(),
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'cluster', {
    header: 'Cluster',
    cell: data => {
      const clusterNumber = data.getValue()?.number
      if (!clusterNumber) {
        return '-'
      }
      return h('span', [
        h(Anchor, {
          href: `/clusters/${clusterNumber}`,
          class: "inline-flex items-center gap-1 text-blue-600"
        }, () => [
          h(Icon, { name: "pajamas:group", class: "h-5 w-5" }),
          clusterNumber
        ])
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'assignmentSet',
    {
      header: 'Assignees',
      cell: (data) => {
        const assignments = data.getValue()
        if (!assignments) {
          return 'No assignments'
        }

        const rfcToBeId = data.row.original.id
        if (rfcToBeId === undefined) {
          throw Error(`Internal error: expected queueItem to have id but was ${JSON.stringify(data.row.original)}`)
        }

        const listItems: VNode[] = []

        const assignmentsByRoles = groupBy(
          assignments,
          (assignment) => assignment.role
        )

        const orderedRoles = Object.keys(assignmentsByRoles)
          .sort((a, b) => a.localeCompare(b, 'en'))

        for (const role of orderedRoles) {
          const assignmentsOfRole = assignmentsByRoles[role] ?? []

          const redundantAssignmentsOfSamePersonToSameRole = assignmentsOfRole.filter((assignment, _index, arr) => {
            const { person } = assignment
            if (person === undefined || person == null) {
              return false
            }
            const firstAssignmentOfPersonToRole = arr.find(arrAssignment => assignment.person && arrAssignment.person && arrAssignment.person === assignment.person)
            if (!firstAssignmentOfPersonToRole) {
              console.log(`Couldn't find first assignment for person #${assignment.person} in`, arr)
              throw Error(`Internal error. Should be able to find first assignment for person #${assignment.person}. See console`)
            }
            // the first assignment of person in the list of assignments should always match the current assignment of person
            // because there shouldn't be duplicate/redundant assignments
            // but if the id is different then it is a redundant assignment,
            // so we'll prompt the user to delete them
            return assignment.id !== firstAssignmentOfPersonToRole.id
          })

          listItems.push(h('li', { class: 'flex gap-3' }, [
            h('span',
              h(BaseBadge, { label: role, class: 'mr-1' })),
            h('ul', { class: 'flex flex-col gap-2' }, [
              ...assignmentsOfRole.map(assignment => {
                const rpcPerson = people.value.find((p) => p.id === assignment.person)
                return h(Anchor, {
                  href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
                  class: [ANCHOR_STYLE, 'text-sm nowrap']
                }, () => [
                  rpcPerson ? rpcPerson.name : pending ? `...` : '(unknown person)',
                ])
              }).reduce((acc, item, index, arr) => {
                // add commas between items
                const listItemChildren = []
                listItemChildren.push(item)
                if (index < arr.length - 1) {
                  listItemChildren.push(', ')
                } else {
                  listItemChildren.push(' ')
                }
                const listItem = h('li', listItemChildren)
                acc.push(listItem)
                return acc
              }, [] as (VNode | string)[])]),
          ]))
        }

        return h('ul', { class: 'flex flex-col gap-x-1 gap-y-3' }, listItems)
      },
      enableSorting: false,
    }
  ),
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return queueItems.value
  },
  columns,
  initialState: {
    globalFilter: () => true, // a truthy value is needed to trigger globalFilterFn below
  },
  enableFilters: true,
  globalFilterFn: (row) => {
    if (!props.name) {
      return true
    }
    return row.original.name === props.name
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  state: {
    get sorting() {
      return sorting.value
    },
  },
  onSortingChange: updaterOrValue => {
    sorting.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(sorting.value) : updaterOrValue
  }
})

const { data: people, status: peopleStatus, error: peopleError } = await useAsyncData(() => api.rpcPersonList(), {
  server: false,
  lazy: true,
  default: () => [] as RpcPerson[]
})
</script>
