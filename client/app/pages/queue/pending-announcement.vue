<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
    </TitleBlock>

    <QueueTabs :current-tab="currentTab" />

    <ErrorAlert v-if="error">
      {{ error }}
    </ErrorAlert>

    <div class="p-2">
      <RpcTable>
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
import type { PaginatedRfcToBeList } from '~/purple_client'
import { type QueueTabId } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'
import BaseButton from '~/components/BaseButton.vue'
import { overlayModalKey } from '~/providers/providerKeys'

const api = useApi()

const overlayModal = inject(overlayModalKey)

const currentTab: QueueTabId = 'pending-announcement'

type Row = PaginatedRfcToBeList["results"][number]

const {
  data,
  pending,
  refresh,
  status,
  error,
} = await useAsyncData(
  'queue2-pending-announcement',
  () => api.documentsList({ }),
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
  columnHelper.accessor('rfcNumber', {
    header: 'RFC',
    cell: data => {
      return h('span', { class: 'px-3 py-4 text-gray-500 dark:text-neutral-400' }, `RFC ${data.getValue()}`)
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
    id: 'icon',
    header: '',
    cell: (data) => {
      const row = data.row.original
      const { id, name } = row
      if (!id || !name) {
        console.error({ rfcToBe: row })
        throw Error('Expected rfcToBe to have id and name but some were undefined. See console.')
      }

      return h(
        BaseButton,
        {
          btnType: 'default',
          size: 'xs',
          onClick: async () => {
            if(!overlayModal) {
              console.error({ overlayModal })
              throw Error('Expected overlayModal to be available. See console.')
            }
            isLoadingByRfcToBeId.value[id.toString()] = true
            await openEmailModal({
              api,
              rfcToBeId: id,
              draftName: name,
              overlayModal,
              mailTemplateSort: (a, b) => {
                if (a.template.msgtype === 'publication') {
                  return -1
                }
                if (b.template.msgtype === 'publication') {
                  return 1
                }
                return 0
              }
            })
            isLoadingByRfcToBeId.value[id.toString()] = false
          }
        },
        [
          "Announce publication",
          isLoadingByRfcToBeId.value[id.toString()]
            ? h(Icon, { name: 'ei:spinner-3', size: '1rem', class: 'animate-spin' })
            : undefined
        ]
      )
    }
  }),
]

const isLoadingByRfcToBeId = ref<Record<string, boolean>>({})

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
