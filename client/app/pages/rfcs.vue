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
import { snackbarForErrors } from "~/utils/snackbar"
import { BaseButton, Icon } from '#components'

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

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleDateString()
}

const overlayModal = inject(overlayModalKey)

// Delete confirmation component
const DeleteConfirmModal = defineComponent({
  props: {
    rfcNumber: {
      type: Number,
      required: true
    }
  },
  emits: ['success', 'close'],
  setup(props, { emit }) {
    const isDeleting = ref(false)

    const deleteRfcNumber = async () => {
      try {
        isDeleting.value = true

        await api.unusableRfcNumbersDestroy({
          number: props.rfcNumber
        })

        snackbar.add({
          type: 'success',
          title: `RFC ${props.rfcNumber} removed from unusable numbers`,
          text: ''
        })

        emit('success')
        emit('close')

      } catch (e: unknown) {
        snackbarForErrors({
          snackbar,
          defaultTitle: 'Unable to delete RFC number',
          error: e
        })
      } finally {
        isDeleting.value = false
      }
    }

    return () => h('div', { class: 'flex flex-col h-full bg-white dark:bg-gray-800' }, [
      h('div', { class: 'flex-shrink-0 px-4 py-6 sm:px-6' }, [
        h('div', { class: 'flex items-start justify-between space-x-3' }, [
          h('div', { class: 'space-y-1' }, [
            h('h2', { class: 'text-lg font-medium text-gray-900 dark:text-white' },
            'Delete RFC Number'),
            h('p', { class: 'text-sm text-gray-500 dark:text-gray-400' },
            `Are you sure you want to delete RFC ${props.rfcNumber} from the unusable ` +
            `numbers list?`)
          ])
        ])
      ]),

      h('div', { class: 'flex-shrink-0 px-4 py-6 sm:px-6' }, [
        h('div', { class: 'flex justify-end space-x-3' }, [
          h(BaseButton, {
            type: 'button',
            variant: 'secondary',
            onClick: () => emit('close')
          }, 'Cancel'),
          h(BaseButton, {
            type: 'button',
            variant: 'danger',
            disabled: isDeleting.value,
            onClick: deleteRfcNumber
          }, isDeleting.value ? 'Deleting...' : 'Delete RFC Number')
        ])
      ])
    ])
  }
})

const AddNumberForm = defineComponent({
  emits: ['success', 'close'],
  setup(_, { emit }) {
    const newRfcNumber = ref<number | null>(null)
    const newComment = ref('')
    const isSubmitting = ref(false)

    const addUnusableRfcNumber = async () => {
      if (!newRfcNumber.value) return

      try {
        isSubmitting.value = true

        await api.unusableRfcNumbersCreate({
          unusableRfcNumberRequest : {
            number: newRfcNumber.value,
            comment: newComment.value || ''
          }
        })

        snackbar.add({
          type: 'success',
          title: `RFC ${newRfcNumber.value} added to unusable numbers`,
          text: ''
        })

        emit('success')
        emit('close')

      } catch (e: unknown) {
        snackbarForErrors({
          snackbar,
          defaultTitle: 'Unable to add RFC number',
          error: e
        })
        console.error(e)
      } finally {
        isSubmitting.value = false
      }
    }

    return () => h('form', {
      onSubmit: (e: Event) => {
        e.preventDefault()
        addUnusableRfcNumber()
      },
      class: 'space-y-6'
    }, [
      h('div', [
        h('label', {
          for: 'rfc-number',
          class: 'block text-sm font-medium text-gray-700 dark:text-gray-300'
        }, 'RFC Number *'),
        h('input', {
          id: 'rfc-number',
          type: 'number',
          required: true,
          min: 1,
          value: newRfcNumber.value,
          onInput: (e: Event) => {
            const target = e.target as HTMLInputElement
            newRfcNumber.value = target.value ? parseInt(target.value) : null
          },
          placeholder: 'Enter RFC number',
          class: 'mt-1 block w-full px-3 py-2 border border-gray-300 ' +
          'dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 ' +
          'focus:outline-none focus:ring-blue-500 focus:border-blue-500 ' +
          'dark:bg-gray-700 dark:text-white'
        })
      ]),

      h('div', [
        h('label', {
          for: 'comment',
          class: 'block text-sm font-medium text-gray-700 dark:text-gray-300'
        }, 'Comment'),
        h('textarea', {
          id: 'comment',
          rows: 4,
          value: newComment.value,
          onInput: (e: Event) => {
            const target = e.target as HTMLTextAreaElement
            newComment.value = target.value
          },
          placeholder: 'Enter reason for making this RFC number unusable...',
          class: 'mt-1 block w-full px-3 py-2 border border-gray-300 ' +
          'dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 ' +
          'focus:outline-none focus:ring-blue-500 focus:border-blue-500 ' +
          'dark:bg-gray-700 dark:text-white'
        })
      ]),

      h('div', { class: 'flex justify-end space-x-3 pt-6' }, [
        h(BaseButton, {
          type: 'button',
          variant: 'secondary',
          onClick: () => emit('close')
        }, 'Cancel'),
        h(BaseButton, {
          type: 'submit',
          disabled: isSubmitting.value || !newRfcNumber.value
        }, isSubmitting.value ? 'Adding...' : 'Add Number')
      ])
    ])
  }
})

const openDeleteConfirmModal = (rfcNumber: number) => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }

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
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }

  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: h('div', { class: 'flex flex-col h-full bg-white dark:bg-gray-800' }, [
      h('div', { class: 'flex-shrink-0 px-4 py-6 sm:px-6' }, [
        h('div', { class: 'flex items-start justify-between space-x-3' }, [
          h('div', { class: 'space-y-1' }, [
            h('h2', { class: 'text-lg font-medium text-gray-900 dark:text-white' },
            'Add Unusable RFC Number'),
            h('p', { class: 'text-sm text-gray-500 dark:text-gray-400' },
            'Reserve an RFC number to make it unavailable for assignment.')
          ])
        ])
      ]),

      h('div', { class: 'flex-1 px-4 sm:px-6' }, [
        h(AddNumberForm, {
          onSuccess: () => refresh(),
          onClose: () => overlayModal.closeOverlayModal()
        })
      ])
    ]),
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
