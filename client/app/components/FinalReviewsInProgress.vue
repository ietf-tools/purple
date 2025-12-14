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
import { Anchor, Icon } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
  type SortingState,
} from '@tanstack/vue-table'
import type { QueueItem, RpcPerson } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import type { HeadingLevel } from '~/utils/html'

type Props = {
  name?: string
  headingLevel?: HeadingLevel
  people: RpcPerson[]
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
      return h(Anchor, { href: `${documentPathBuilder(data.row.original)}#final-review`, 'class': ANCHOR_STYLE }, () => [
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
      return columnFormatterCluster(clusterNumber)
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'assignmentSet',
    {
      header: 'Assignees',
      cell: (data) => {
        const assignments = data.getValue()
        return columnFormatterAssignments({
          assignments,
          rfcToBeId: data.row.original.id,
          people: props.people,
          queueItemsIsPending: pending.value,
          rowForDebug: data.row.original
        })
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


</script>
