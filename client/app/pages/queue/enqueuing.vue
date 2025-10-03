<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
      <template #right>
        <QueueTitleRight />
      </template>
    </TitleBlock>

    <QueueTabs :current-tab="currentTab" @pending="pending" @refresh="refresh" />

    <ErrorAlert v-if="error">
      {{ error }}
    </ErrorAlert>

    <div class="p-2">
      <RpcTable>
        <RpcThead>
          <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <RpcTh
              v-for="header in headerGroup.headers"
              :key="header.id"
              :colSpan="header.colSpan"
              :is-sortable="header.column.getCanSort()"
              :sort-direction="header.column.getIsSorted()"
              @click="header.column.getToggleSortingHandler()?.($event)"
            >
              <div class="flex items-center gap-2">
                <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                  :props="header.getContext()" />
                <Transition name="sort-indicator">
                  <Icon
                    v-if="header.column.getCanSort()"
                    name="heroicons:arrows-up-down"
                    class="text-gray-400 opacity-60 hover:opacity-100"
                  />
                </Transition>
              </div>
            </RpcTh>
          </tr>
        </RpcThead>
        <RpcTbody>
          <RpcRowMessage :status="status" :column-count="table.getAllColumns().length" :row-count="table.getRowModel().rows.length" />
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
import type { QueueItem } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import type { TabId } from '~/utils/queue'

const api = useApi()

const currentTab: TabId = 'enqueuing'

const {
  data,
  pending,
  status,
  refresh,
  error,
} = await useAsyncData(
  'queue2-enqueuing',
  () => api.queueList(),
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
      return h(Anchor, { href: `/docs/${data.row.original.name}/enqueue`, 'class': ANCHOR_STYLE }, () => [
        data.getValue(),
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'labels', {
    header: 'Labels',
    cell: _data => '',
    enableSorting: false,
  }),
  columnHelper.accessor(
    'pages', {
    header: 'Pages',
    cell: data => data.getValue(),
    sortingFn: 'alphanumeric',
  })
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  initialState: {
    globalFilter: () => true, // a truthy value is needed to trigger globalFilterFn below
  },
  enableFilters: true,
  globalFilterFn: (row) => {
    return row.original.disposition === 'created'
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
