<template>
  <div class="container mx-auto p-6">
    <div class="mb-6 flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Unusable RFC Numbers
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          RFC numbers that have been reserved or are otherwise unavailable for
          assignment.
        </p>
      </div>
      <BaseButton @click="openAddNumberModal" class="ml-4">
        Add Number
      </BaseButton>
    </div>

    <div v-if="pending" class="flex justify-center py-8">
      <div class="text-gray-500">Loading unusable RFC numbers...</div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
      <div class="text-red-800">
        <h3 class="font-medium">Error loading unusable RFC numbers</h3>
        <p class="mt-1 text-sm">{{ error }}</p>
      </div>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
      <div v-if="unusableRfcs.length === 0" class="p-6 text-center text-gray-500">
        No unusable RFC numbers found.
      </div>

      <div v-else>
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 w-12"></th>
              <th
                v-for="header in table.getHeaderGroups()[0]?.headers"
                :key="header.id"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
              >
                <div
                  v-if="header.column.getCanSort()"
                  class="flex items-center cursor-pointer hover:text-gray-700 dark:hover:text-gray-200"
                  @click="header.column.getToggleSortingHandler()?.($event)"
                >
                  <FlexRender
                    :render="header.column.columnDef.header"
                    :props="header.getContext()"
                  />
                  <Icon
                    v-if="header.column.getIsSorted() === 'asc'"
                    name="heroicons:chevron-up"
                    class="ml-1 h-3 w-3"
                  />
                  <Icon
                    v-else-if="header.column.getIsSorted() === 'desc'"
                    name="heroicons:chevron-down"
                    class="ml-1 h-3 w-3"
                  />
                  <Icon
                    v-else
                    name="heroicons:chevron-up-down"
                    class="ml-1 h-3 w-3 opacity-50"
                  />
                </div>
                <FlexRender
                  v-else
                  :render="header.column.columnDef.header"
                  :props="header.getContext()"
                />
              </th>
            </tr>
          </thead>

          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="row in table.getRowModel().rows"
              :key="row.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700 group"
            >
              <td class="px-6 py-4 w-12">
                <button
                  @click="openDeleteConfirmModal(row.original.number)"
                  class="text-red-400 hover:text-red-600 opacity-50 group-hover:opacity-100 transition-opacity"
                  title="Delete RFC number"
                >
                  <Icon name="heroicons:x-mark" class="h-4 w-4" />
                </button>
              </td>
              <td
                v-for="cell in row.getVisibleCells()"
                :key="cell.id"
                class="px-6 py-4 align-top"
              >
                <FlexRender
                  :render="cell.column.columnDef.cell"
                  :props="cell.getContext()"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="unusableRfcs.length > 0" class="bg-gray-50 dark:bg-gray-700 px-6 py-3 border-t border-gray-200 dark:border-gray-600">
        <div class="text-sm text-gray-600 dark:text-gray-300">
          Total: {{ unusableRfcs.length }} unusable RFC number{{ unusableRfcs.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>

    <!-- Refresh button -->
    <div class="mt-6 flex justify-end">
      <button
        @click="refresh"
        :disabled="pending"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <Icon name="heroicons:arrow-path" class="h-4 w-4 mr-2" />
        Refresh
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UnusableRfcNumber } from '~/purple_client'
import {
  createColumnHelper,
  FlexRender,
  getCoreRowModel,
  getSortedRowModel,
  useVueTable,
  type SortingState,
} from '@tanstack/vue-table'
import { overlayModalKey } from '~/providers/providerKeys'
import { BaseButton, Icon } from '#components'
import AddConfirmModal from '~/components/UnusableRfcNumberAdd.vue'
import DeleteConfirmModal from '~/components/UnusableRfcNumberDelete.vue'
import type { DateTime } from 'luxon'

const api = useApi()
const snackbar = useSnackbar()

const {
  data: unusableRfcs,
  pending,
  error,
  refresh,
} = await useAsyncData(
  'unusable-rfc-numbers',
  () => api.unusableRfcNumbersList(),
  {
    server: false,
    lazy: true,
    default: () => [] as UnusableRfcNumber[],
  }
)

const formatDate = (dateString: DateTime | undefined) => {
  if (!dateString) return 'Unknown'
  return dateString.toLocaleString()
}

const overlayModal = inject(overlayModalKey)
  if (!overlayModal) {
    throw Error('Expected injection of overlayModalKey')
  }

const openDeleteConfirmModal = (rfcNumber: number) => {
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: h(DeleteConfirmModal, {
      rfcNumber: rfcNumber,
      onSuccess: () => refresh(),
      onClose: () => overlayModal.closeOverlayModal()
    }),
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {

    } else {
      console.error(e)
      throw e
    }
  })
}

const openAddNumberModal = () => {
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: h(AddConfirmModal, {
        onSuccess: () => refresh(),
        onClose: () => overlayModal.closeOverlayModal()
    }),
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {

    } else {
      console.error(e)
      throw e
    }
  })
}

// Table setup
const columnHelper = createColumnHelper<UnusableRfcNumber>()

const columns = [
  columnHelper.accessor('number', {
    header: 'RFC Number',
    cell: data => h('span', {
      class: 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ' +
      'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }, `RFC ${data.getValue()}`),
    sortingFn: (rowA, rowB, columnId) => {
      const a = Number(rowA.getValue(columnId))
      const b = Number(rowB.getValue(columnId))
      return a - b
    },
  }),
  columnHelper.accessor('comment', {
    header: 'Comment',
    cell: data => h('div', {
      class: 'text-sm text-gray-900 dark:text-white max-w-md break-words'
    }, data.getValue() || 'No comment provided'),
    enableSorting: false,
  }),
  columnHelper.accessor('createdAt', {
    header: 'Created At',
    cell: data => h('div', {
      class: 'text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap'
    }, `Reserved on ${formatDate(data.getValue())}`),
    sortingFn: (rowA, rowB, columnId) => {
      const a = new Date(rowA.getValue(columnId) || 0)
      const b = new Date(rowB.getValue(columnId) || 0)
      return a.getTime() - b.getTime()
    },
  }),
]

const sorting = ref<SortingState>([{ id: 'number', desc: false }])

const table = useVueTable({
  get data() {
    return unusableRfcs.value || []
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
    sorting.value = typeof updaterOrValue === 'function'
      ? updaterOrValue(sorting.value)
      : updaterOrValue
  },
})

useHead({
  title: 'Unusable RFC Numbers',
  meta: [
    { name: 'description', content: 'List of RFC numbers that are reserved or ' +
    'unavailable for assignment' }
  ]
})
</script>
