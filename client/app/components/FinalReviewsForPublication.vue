<template>
  <div>
    <Heading :heading-level="props.headingLevel" class="mt-5">
      For PUB {{ props.status === 'success' ? `(${props.queueItems.length})` : '' }}
    </Heading>

    <div v-if="availableLabels.length" class="flex flex-wrap gap-1 mb-2">
      <button v-for="label in availableLabels" :key="label.slug"
        :class="['rounded', selectedLabels.has(label.slug) ? 'opacity-100' : 'opacity-40']"
        type="button" @click="toggleLabel(label.slug)">
        <RpcLabel :label="label" />
      </button>
    </div>
    <RpcTable>
      <colgroup>
        <col class="w-8">
        <col>
        <col class="w-40">
        <col class="w-28">
        <col class="w-28">
        <col class="w-28">
        <col class="w-96">
      </colgroup>
      <RpcThead>
        <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
            :is-sortable="header.column.getCanSort()" :sort-direction="header.column.getIsSorted()"
            :column-name="getVNodeText(header.column.columnDef.header)" @click="header.column.getToggleSortingHandler()?.($event)">
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
import type { AsyncDataRequestStatus, NuxtError } from '#app'
import { Anchor, Icon, RpcLabel } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
  type SortingState,
} from '@tanstack/vue-table'
import type { Label, QueueItem, RpcPerson } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import type { HeadingLevel } from '~/utils/html'

type Props = {
  queueItems: QueueItem[]
  error?: NuxtError<unknown>
  status: AsyncDataRequestStatus
  headingLevel?: HeadingLevel
  people: RpcPerson[]
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 2 })

const selectedLabels = ref<Set<string>>(new Set())

const availableLabels = computed<Label[]>(() => {
  const seen = new Set<string>()
  const labels: Label[] = []
  for (const item of props.queueItems) {
    for (const label of item.labels ?? []) {
      if (!seen.has(label.slug)) {
        seen.add(label.slug)
        labels.push(label)
      }
    }
  }
  return labels.sort((a, b) => a.slug.localeCompare(b.slug))
})

const toggleLabel = (slug: string) => {
  const next = new Set(selectedLabels.value)
  if (next.has(slug)) next.delete(slug)
  else next.add(slug)
  selectedLabels.value = next
}

const filteredItems = computed(() =>
  selectedLabels.value.size === 0
    ? props.queueItems
    : props.queueItems.filter(item =>
        item.labels?.some(l => selectedLabels.value.has(l.slug))
      )
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
      return h(Anchor, { href: `${documentPathBuilder(data.row.original)}approvals`, 'class': ANCHOR_STYLE }, () => [
        data.getValue(),
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('labels', {
    header: 'Labels',
    cell: data => {
      const labels = data.getValue()
      if (!labels?.length) return undefined
      return h('span', labels.map((label: Label) => h(RpcLabel, { label, class: 'mr-1' })))
    },
    enableSorting: false,
  }),
  columnHelper.accessor('rfcNumber', {
    header: 'RFC Number',
    cell: data => data.getValue(),
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('finalApproval', {
    header: 'Approvals Received',
    cell: data => {
      const approvals = data.getValue()
      if (!approvals?.length) return undefined
      const approved = approvals.filter(a => a.approved !== null).length
      return `${approved}/${approvals.length}`
    },
    enableSorting: false,
  }),
  columnHelper.accessor(
    'cluster', {
    header: 'Cluster',
    cell: data => {
      const clusterNumber = data.getValue()?.number
      return columnFormatterCluster(clusterNumber)
    },
    sortingFn: (rowA, rowB, columnId) => {
      const a = (rowA.getValue(columnId) as { number?: number } | null)?.number ?? -1
      const b = (rowB.getValue(columnId) as { number?: number } | null)?.number ?? -1
      return a - b
    },
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
          queueItemsIsPending: props.status === 'pending',
          blockingReasons: data.row.original.blockingReasons,
          rowForDebug: data.row.original
        })
      },
      sortingFn: (rowA, rowB, columnId) =>
        sortAssignees(rowA.getValue(columnId), props.people)
          .localeCompare(sortAssignees(rowB.getValue(columnId), props.people)),
    }
  ),
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return filteredItems.value
  },
  columns,
  initialState: {
    globalFilter: () => true, // a truthy value is needed to trigger globalFilterFn below
  },
  enableFilters: true,
  globalFilterFn: (row) => {
    return true
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
