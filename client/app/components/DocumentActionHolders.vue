<template>
  <ErrorAlert v-if="error" title="API Error for Action Holders">
    {{ error }}
  </ErrorAlert>

  <BaseCard>
    <template #header>
      <CardHeader title="Action Holders">
        <template #actions>
          <BaseButton @click="openAddModal()" title="Add action holder">Add</BaseButton>
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
import {
  createColumnHelper,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useVueTable,
  FlexRender,
} from '@tanstack/vue-table'
import { DateTime } from 'luxon'
import type { SortingState } from '@tanstack/vue-table'
import type { ActionHolder, BaseDatatrackerPerson } from '~/purple_client'
import DocumentActionHolderEditModal from './DocumentActionHolderEditModal.vue'
import DocumentActionHolderAddModal from './DocumentActionHolderAddModal.vue'
import { overlayModalKey } from '~/providers/providerKeys'
import { ANCHOR_STYLE } from '~/utils/html'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'

type Props = {
  name: string
  headingLevel?: HeadingLevel
  onSuccess?: () => Promise<void>
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 2 })

const api = useApi()
const datatrackerLinks = useDatatrackerLinks()

const {
  data: actionHoldersList,
  status,
  refresh,
  error,
} = await useAsyncData(
  `action-holders-for-${props.name}`,
  () => api.documentsActionHoldersList({ draftName: props.name }),
  {
    server: false,
    lazy: true,
    default: () => [] as ActionHolder[],
  }
)

const formatAuthor = (person: BaseDatatrackerPerson | undefined): VNode => {
  if (!person) return h('i', '(unknown)')
  return h('span', [
    h('a', { href: person.email ? datatrackerLinks.personByEmail(person.email) : undefined, class: ANCHOR_STYLE }, [
      person.name ?? '(unknown)',
      h('span', { class: 'font-normal text-gray-700 dark:text-gray-200' }, person.email ? ` #${person.email}` : ''),
    ]),
  ])
}

const reloadEverything = async () => {
  refresh()
  await props.onSuccess?.()
}

const columnHelper = createColumnHelper<ActionHolder>()

const columns = [
  columnHelper.accessor('person', {
    header: 'Approver Name',
    cell: data => formatAuthor(data.getValue()),
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('comment', {
    header: 'Comment',
    cell: data => {
      const comment = data.getValue()
      if (!comment) return ''
      const truncated = comment.length > 40 ? comment.substring(0, 40) + '...' : comment
      return h('span', { class: 'text-sm', title: comment }, truncated)
    },
  }),
  columnHelper.accessor(
    'sinceWhen', {
    header: 'Date Requested',
    cell: data => {
      const date = data.getValue()
      if (!date) {
        return '(N/A)'
      }
      const dateTime = DateTime.fromJSDate(date)
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
      const completed = data.row.original.completed
      if (completed) {
        const dateTime = DateTime.fromJSDate(completed)
        return h('div', { class: 'flex flex-row items-center gap-1' }, [
          h(Icon, { name: 'duo-icons:approved', size: '1.25em', class: 'text-green-500' }),
          h('time', { datetime: dateTime.toISO(), class: 'text-green-700 text-sm' },
            dateTime.toLocaleString(DateTime.DATE_MED)),
        ])
      }
      return h('div', { class: 'flex flex-row items-center gap-1' }, [
        h(Icon, { name: 'emojione:hourglass-not-done', size: '1.25em', class: 'text-gray-400' }),
        h('span', { class: 'text-gray-600 text-sm' }, 'Pending'),
      ])
    },
  }),
  columnHelper.accessor('deadline', {
    header: 'Deadline',
    cell: data => {
      const date = data.getValue()
      if (!date) return h('span', { class: 'text-gray-400' }, '(none)')
      const dateTime = DateTime.fromJSDate(date)
      return h('time', { datetime: dateTime.toISO() }, dateTime.toLocaleString(DateTime.DATE_MED))
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor('body', {
    header: 'Body',
    cell: data => {
      const body = data.getValue()
      if (!body) return h('span', { class: 'text-gray-400' }, '(none)')
      return h('span', { class: 'text-sm', title: body }, body.length > 40 ? body.substring(0, 40) + '...' : body)
    },
    sortingFn: 'alphanumeric',
  }),

  columnHelper.display({
    id: 'action',
    header: 'Action',
    cell: data => {
      return h(
        BaseButton,
        {
          btnType: 'default',
          size: 'xs',
          title: 'Edit action holder',
          onClick: () => openEditModal(data.row.original),
        },
        () => 'Edit'
      )
    },
  }),
]

const sorting = ref<SortingState>([])

const table = useVueTable({
  get data() {
    return actionHoldersList.value
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
        ? updaterOrValue(sorting.value)
        : updaterOrValue
  },
})

const overlayModal = inject(overlayModalKey)

const openAddModal = () => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: DocumentActionHolderAddModal,
    componentProps: {
      draftName: props.name,
      onSuccess: reloadEverything,
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // modal closed normally
    } else {
      console.error(e)
      throw e
    }
  })
}

const openEditModal = (actionHolder: ActionHolder) => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: DocumentActionHolderEditModal,
    componentProps: {
      actionHolder,
      draftName: props.name,
      onSuccess: reloadEverything,
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // modal closed normally
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
