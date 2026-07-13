<template>
  <ErrorAlert v-if="error" title="API Error for Done / PUB">
    {{ error }}
  </ErrorAlert>

  <BaseCard>
    <template #header>
      <CardHeader title="Final Reviews">
        <template v-if="queueUrl" #titleSuffix>
          <span class="inline-flex items-center gap-2 text-sm font-normal">
            <button
              type="button"
              class="inline-flex items-center text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"
              :title="`Copy queue link: ${queueUrl}`"
              @click="copyQueueUrl"
            >
              <Icon name="heroicons:clipboard-document" size="1em" />
            </button>
            <a
              :href="queueUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
            >
              Queue Page
              <Icon name="heroicons:arrow-top-right-on-square" size="1em" />
            </a>
          </span>
        </template>
        <template #actions>
          <BaseButton @click="openAddModal()" title="Add Final Review approver">Add</BaseButton>
        </template>
      </CardHeader>
    </template>

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
        <RpcRowMessage :status="status" :column-count="table.getAllColumns().length"
          :row-count="table.getRowModel().rows.length" />
        <tr v-for="row in table.getRowModel().rows" :key="row.id">
          <RpcTd v-for="cell in row.getVisibleCells()" :key="cell.id">
            <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
          </RpcTd>
        </tr>
      </RpcTbody>
    </RpcTable>
  </BaseCard>
</template>

<script setup lang="ts">
import { Icon, BaseButton } from '#components'
import { createColumnHelper, getCoreRowModel, getFilteredRowModel, getSortedRowModel, useVueTable, FlexRender } from '@tanstack/vue-table'
import { DateTime } from 'luxon'
import type { SortingState } from '@tanstack/vue-table'
import type { BaseDatatrackerPerson, FinalApproval } from '~/purple_client'
import DocumentFinalReviewModal from './DocumentFinalReviewModal.vue'
import { overlayModalKey } from '~/providers/providerKeys'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'
import { useQueueLinks } from '~/composables/useQueueLinks'
import { copyToClipboard } from '~/utils/clipboard'

type Props = {
  name: string
  rfcNumber?: number | null
  headingLevel?: HeadingLevel
  onSuccess?: () => Promise<void>
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 2 })

const api = useApi()
const datatrackerLinks = useDatatrackerLinks()
const snackbar = useSnackbar()
const queueLinks = useQueueLinks()

// Link to the public final-review queue page, only when an RFC number is assigned.
const queueUrl = computed(() =>
  props.rfcNumber != null ? queueLinks.finalReview(props.rfcNumber) : null
)

const copyQueueUrl = async () => {
  if (!queueUrl.value) return
  const copied = await copyToClipboard(queueUrl.value)
  snackbar.add({
    type: copied ? 'success' : 'error',
    title: copied ? 'Queue link copied' : 'Could not copy link',
    text: copied ? queueUrl.value : '',
  })
}

const {
  data: finalApprovalsList,
  pending,
  status,
  refresh,
  error,
} = await useAsyncData(
  'final-review-for-document',
  () => api.documentsFinalApprovalsList({ draftName: props.name }),
  {
    server: false,
    lazy: true,
    default: () => [] as FinalApproval[],
  }
)

const reloadEverything = () => {
  refresh()
  props.onSuccess?.()
}

const columnHelper = createColumnHelper<FinalApproval>()

const columns = [
  columnHelper.accessor('approver.name', {
    header: 'Approver Name',
    cell: data => {
      const rowOriginal = data.row.original
      const { approver } = rowOriginal
      if (!approver) {
        return h('i', '(no approver)')
      }

      const formatAuthor = (author: BaseDatatrackerPerson): VNode => {
        return h('span', [
          h('a', { href: author.email ? datatrackerLinks.personByEmail(author.email) : undefined, class: ANCHOR_STYLE }, [
            `${author.name}`,
            h('span', { class: 'font-normal text-gray-700 dark:text-gray-200' }, ` #${author.email}`)
          ]),
        ])
      }

      const approverVNode = formatAuthor(approver)
      if (!rowOriginal.overridingApprover) {
        return h('span', [
          approverVNode,
        ])
      }
      return h('span', [
        formatAuthor(rowOriginal.overridingApprover),
        ' on behalf of ',
        approverVNode
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'comment', {
    header: 'Comment',
    cell: data => {
      const comment = data.getValue()
      if (!comment) {
        return ''
      }
      const truncated = comment.length > 30 ? comment.substring(0, 30) + '...' : comment
      return h('span', { class: 'text-sm', title: comment }, truncated)
    },
  }),
  columnHelper.accessor(
    'requested', {
    header: 'Date Requested',
    cell: data => {
      const date = data.getValue()
      if (!date) {
        return '(N/A)'
      }
      const dateTime = DateTime.fromJSDate(date, { zone: 'utc' })
      return h('time', { datetime: dateTime.toString() }, dateTime.toLocaleString(
        DateTime.DATE_MED_WITH_WEEKDAY
      ))
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.display({
    id: 'status',
    header: 'Approval Status',
    cell: data => {
      const status = finalApprovalToStatus(data.row.original)
      switch (status) {
        case 'approved':
          return h('div', { class: 'flex flex-row items-center' }, [h(Icon, { name: "duo-icons:approved", size: "1.25em", class: "text-green-400 dark:text-neutral-500 mr-2" }), 'Approved'])
        case 'pending':
          return h('div', { class: 'flex flex-row items-center' }, [h(Icon, { name: "emojione:hourglass-not-done", size: "1.25em", class: "text-gray-400 dark:text-neutral-500 mr-2" }), 'Pending'])
      }
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'approved', {
    header: 'Date Approved',
    cell: data => {
      const date = data.getValue()
      if (!date) {
        return '(N/A)'
      }
      const dateTime = DateTime.fromJSDate(date, { zone: 'utc' })
      return h('time', { datetime: dateTime.toString() }, dateTime.toLocaleString(
        DateTime.DATE_MED_WITH_WEEKDAY
      ))
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.display({
    id: 'action',
    header: 'Action',
    cell: (data) => {
      return h(BaseButton, { btnType: 'default', size: 'xs', title: `Edit Final Review approver`, 'onClick': () => openEditModal(data.row.original) }, () => 'Edit')
    }
  }),
]

type FinalApprovalStatus = 'pending' | 'approved'

const finalApprovalToStatus = (finalApproval: FinalApproval): FinalApprovalStatus => {
  if (finalApproval.approved) {
    return 'approved'
  }
  if (finalApproval.requested) {
    return 'pending'
  }
  console.error('Unable to convert finalApproval', finalApproval)
  throw Error('Unable to convert finalApproval. See console.')
}

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return finalApprovalsList.value
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

const overlayModal = inject(overlayModalKey)

const openEditModal = (finalApproval: FinalApproval) => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: DocumentFinalReviewModal,
    componentProps: {
      finalApproval,
      name: props.name,
      onSuccess: reloadEverything
    },
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

const openAddModal = () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: DocumentFinalReviewModal,
    componentProps: {
      name: props.name,
      onSuccess: reloadEverything
    },
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}

</script>
