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
            <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
              :is-sortable="header.column.getCanSort()" @click="header.column.getToggleSortingHandler()?.($event)"
              :sort-direction="header.column.getIsSorted()">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
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
import { DateTime } from 'luxon'
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
import type { PaginatedRfcToBeList } from '~/purple_client'
import type { TabId } from '~/utils/queue'

const api = useApi()

const currentTab: TabId = 'published'

type Row = PaginatedRfcToBeList["results"][number]

const {
  data,
  pending,
  refresh,
  status,
  error,
} = await useAsyncData(
  `queue2-published`,
  () => api.documentsList({
    disposition: 'published',
    ordering: '-published_at',
    publishedWithinDays: 30,
  }),
  {
    server: false,
    lazy: true,
    default: () => {
      const defaultValue: PaginatedRfcToBeList = {
        count: 0,
        next: '',
        previous: '',
        results: []
      }
      return defaultValue
    }
  }
)

const columnHelper = createColumnHelper<Row>()

const columns = [
  columnHelper.display({
    id: 'icon',
    header: '',
    cell: () => h(Icon, { name: "uil:file-alt", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" })
  }),
  columnHelper.accessor('name', {
    header: 'RFC',
    cell: data => {
      return h('span', { class: 'px-3 py-4 text-gray-500 dark:text-neutral-400' }, `RFC ${data.row.original.rfcNumber}`)
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('name', {
    header: 'Document',
    cell: data => {
      return h(Anchor, { href: `/docs/${data.row.original.name}`, 'class': ANCHOR_STYLE }, () => [
        data.getValue(),
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.display({
    id: 'labels',
    header: 'Labels',
    cell: _data => '',
  }),
  columnHelper.display({
    id: 'owner', // FIXME: this doesn't exist yet
    header: 'PUB Owner',
    cell: () => 'Unknown'
  }),
  columnHelper.accessor(
    'publishedAt', {
    header: 'Published',
    cell: data => {
      const publishedAt = data.getValue()
      if (!publishedAt) return ''
      return DateTime.fromJSDate(publishedAt).toLocaleString(
        DateTime.DATE_MED_WITH_WEEKDAY
      )
    },
    sortingFn: (rowA, rowB) => sortDate(rowA.original.publishedAt, rowB.original.publishedAt)
  }),
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return data.value.results
  },
  columns,
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
