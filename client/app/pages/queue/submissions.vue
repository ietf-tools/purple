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
import { Anchor, Icon } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getSortedRowModel,
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'
import { DateTime } from 'luxon'
import type { SubmissionListItem } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import { sortDate, type TabId } from '~/utils/queue'

const api = useApi()

const currentTab: TabId = 'submissions'

const {
  data,
  pending,
  refresh,
  status,
  error,
} = await useAsyncData(
  'queue2-submissions',
  () => api.submissionsList(),
  {
    server: false,
    lazy: true,
    default: () => [] as SubmissionListItem[],
  }
)

const columnHelper = createColumnHelper<SubmissionListItem>()

const columns = [
  columnHelper.display(
    {
      id: 'icon',
      header: '',
      cell: _data => {
        return h(Icon, { name: "uil:file-alt", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" })
      }
    }),
  columnHelper.accessor('name', {
    header: 'Document',
    cell: data => {
      return h(Anchor, { href: `/docs/import/?documentId=${data.row.original.id}`, 'class': ANCHOR_STYLE }, () => [
        data.getValue()
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('stream', {
    header: 'Labels',
    cell: _data => '',
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('submitted', {
    header: 'Submitted',
    cell: data =>
      h('span', { class: 'text-xs' }, DateTime.fromJSDate(data.getValue()).toLocaleString(
        DateTime.DATE_MED_WITH_WEEKDAY
      )),
    sortingFn: (rowA, rowB) => sortDate(rowA.original.submitted, rowB.original.submitted)
  })
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  state: {
    get sorting() {
      return sorting.value
    },
  },
  onSortingChange: updaterOrValue => {
    sorting.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(sorting.value)
        : updaterOrValue
  },
})

</script>
