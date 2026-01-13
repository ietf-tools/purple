<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
    </TitleBlock>

    <QueueTabs :current-tab="currentTab" />

    <ErrorAlert v-if="error">
      {{ error }}
    </ErrorAlert>

    <RpcTable>
      <RpcThead>
        <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
            :is-sortable="header.column.getCanSort()" :sort-direction="header.column.getIsSorted()"
            :column-name="getVNodeText(header.column.columnDef.header)"
            @click="header.column.getToggleSortingHandler()?.($event)">
            <div class="flex items-center gap-2">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
            </div>
          </RpcTh>
        </tr>
      </RpcThead>
      <RpcTbody>
        <RpcRowMessage :status="[status]" :column-count="table.getAllColumns().length"
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
import { Anchor, BaseButton, Icon, RpcLabel } from '#components'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'
import type { Label, QueueItem, RfcToBe } from '~/purple_client'
import { type QueueTabId } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'
import { overlayModalKey } from '~/providers/providerKeys'
import PublishModal from '~/components/PublishModal.vue'

const api = useApi()
const currentTab: QueueTabId = 'publish'

const {
  data,
  status,
  pending,
  refresh,
  error,
} = await useAsyncData(
  'queue2-queue',
  () => api.queueList(),
  {
    server: false,
    lazy: true,
    default: () => [] as QueueItem[],
  }
)

const {
  data: labelsData,
  status: labelsStatus,
  pending: labelsPending,
  refresh: labelsRefresh,
  error: labelsError,
} = await useAsyncData(
  'queueList',
  () => api.queueList(),
  {
    server: false,
    lazy: true,
    default: () => [] as Label[],
  }
)

const columnHelper = createColumnHelper<QueueItem>()

const sorting = ref<SortingState>([])

const columns = [
  columnHelper.display({
    id: 'icon',
    header: '',
    cell: () => h(Icon, { name: "uil:file-alt", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" })
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
  columnHelper.accessor('rfcNumber', {
    header: 'RFC Number',
    cell: data => data.getValue(),
    sortingFn: 'alphanumeric',
    sortUndefined: 'last',
  }),
  columnHelper.accessor(
    'labels', {
    header: 'Labels',
    cell: data => {
      const labels = data.getValue()
      if (!labels) return undefined
      return h('span', labels.map(label => h(RpcLabel, { label, class: 'ml-2' })))
    },
    enableSorting: false,
  }),
  columnHelper.accessor(
    'cluster',
    {
      header: 'Cluster',
      cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h(
          Anchor,
          { href: `/clusters/${value.number}` },
          () => [
            h(Icon, { name: 'pajamas:group', class: 'h-5 w-5 inline-block mr-1' }),
            String(value.number)
          ]
        )
      },
      sortingFn: (rowA, rowB) => sortCluster(rowA.original.cluster, rowB.original.cluster),
    }
  ),
  columnHelper.display({
    header: 'Actions',
    cell: (data) => {
      const { original } = data.row
      const { id } = original
      if (!id) {
        console.error({ queueItem: original })
        throw Error("Expected queueItem to have `id`")
      }
      const isLoading = Boolean(isLoadingPublishModal.value[id])
      console.log("isLoadingPublishModal.value[id]", isLoading, isLoadingPublishModal.value[id], isLoadingPublishModal.value, isLoadingPublishModal)
      return h(
        BaseButton,
        { 'onClick': () => openPublishModal(data.row.original), class:"flex items-center" },
        () => [
          h('span', 'Publish'),
          isLoading && h('span', { class: 'w-3' }, [
            h(Icon, { name: 'ei:spinner-3', size:'1.3rem', class: 'animate-spin' })
          ])
        ]
      )
    }
  })
]

const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  state: {
    get sorting() {
      return sorting.value
    },
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  onSortingChange: updaterOrValue => {
    sorting.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(sorting.value)
        : updaterOrValue
  },
})

const isLoadingPublishModal = ref<Record<number, boolean>>({})

const snackbar = useSnackbar()

const overlayModal = inject(overlayModalKey)

const openPublishModal = async (queueItem: QueueItem) => {
  console.log("openPublishModal", queueItem )
  if (!overlayModal) {
    throw Error("Should have overlay modal context")
  }
  if(labelsData.value.length === 0) {
    snackbar.add({
      type: "info",
      text: `Still loading labels, please wait...`
    })
  }

  const { openOverlayModal } = overlayModal

  const { id } = queueItem

  if (!id) {
    console.error({ queueItem })
    throw Error('Expected rfcToBe to have an id')
  }

  isLoadingPublishModal.value = {
    ...isLoadingPublishModal.value,
    [id]: true
  }

  try {
    openOverlayModal({
      component: PublishModal,
      componentProps: {
        queueItem,
        labels: labelsData.value,
        onSuccess: () => { }
      },
    }).catch(e => {
      if (e === undefined) {
        isLoadingPublishModal.value = {
          ...isLoadingPublishModal.value,
          [id]: false
        }
        // ignore... it's just signalling that the modal has closed
      } else {
        console.error(e)
        throw e
      }
    })
  } catch (e) {
    console.error(e)
  }
}

useHead({
  title: 'RPC Publish Queue'
})
</script>
