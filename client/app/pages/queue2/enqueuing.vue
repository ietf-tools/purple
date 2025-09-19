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
            <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
            </RpcTh>
          </tr>
        </RpcThead>
        <RpcTbody>
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
} from '@tanstack/vue-table'
import type { QueueItem } from '~/purple_client'
import type { TabId } from '~/utils/queue'

const api = useApi()

const currentTab: TabId = 'enqueuing'

const {
  data,
  pending,
  refresh,
  error,
} = await useAsyncData(
  `queue2-enqueuing`,
  () => api.queueList(),
  {
    server: false,
    lazy: true,
    default: () => [] as QueueItem[],
  }
)

const columnHelper = createColumnHelper<QueueItem>()

const columns = [
  columnHelper.accessor('name', {
    header: 'Document',
    cell: data => {
      return h(Anchor, { href: `/docs/${data.row.original.name}/enqueue`, 'class': ANCHOR_STYLE }, () => [
        h(Icon, { name: "uil:file-alt", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" }),
        data.getValue(),
      ])
    }
  }),
  columnHelper.accessor(
    // this placeholder column is intentionally empty
    'labels', {
    header: 'Labels',
    cell: _data => ''
  }),
  columnHelper.accessor(
    // this placeholder column is intentionally empty
    'pages', {
    header: 'Submitted',
    cell: _data => ''
  })
]

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
  getFilteredRowModel: getFilteredRowModel()
})

</script>
