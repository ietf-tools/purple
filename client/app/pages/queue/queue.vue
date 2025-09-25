<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
      <template #right>
        <QueueTitleRight />
      </template>
    </TitleBlock>

    <QueueTabs :current-tab="currentTab" @pending="pending" @refresh="refresh" />

    <ErrorAlert v-if="error || peopleError">
      {{ error }} {{ peopleError }}
    </ErrorAlert>

    <div class="flex flex-row gap-x-8 justify-between mb-4">
      <fieldset>
        <legend class="font-bold text-base">
          Filters
          <span class="text-md">&nbsp;</span>
        </legend>
        <div class="flex flex-col gap-1">
          <RpcTristateButton :checked="needsAssignmentTristate"
            @change="(tristate: TristateValue) => needsAssignmentTristate = tristate">
            Needs Assignment?
          </RpcTristateButton>
          <RpcTristateButton :checked="hasExceptionTristate"
            @change="(tristate: TristateValue) => hasExceptionTristate = tristate">
            Has Exception?
          </RpcTristateButton>
        </div>
      </fieldset>
      <fieldset class="flex-1">
        <legend class="font-bold text-sm flex items-end">
          Label filters
          <span class="text-base">&nbsp;</span>
        </legend>
        <div class="grid grid-cols-[repeat(auto-fill,11em)] gap-x-3 gap-y-1">
          <LabelsFilter v-model:all-label-filters="allLabelFilters"
            v-model:selected-label-filters="selectedLabelFilters" />
        </div>
      </fieldset>
    </div>

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
          <RpcRowMessage :status="[status, peopleStatus]" :column-count="table.getAllColumns().length" :row-count="table.getRowModel().rows.length" />
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
import { Anchor, Icon, BaseBadge, RpcLabel } from '#components'
import { DateTime } from 'luxon'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
  sortingFns,
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'
import { groupBy, uniqBy } from 'lodash-es'
import type { Label, QueueItem, RpcPerson } from '~/purple_client'
import { sortDate, type TabId } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'
import { useSiteStore } from '@/stores/site'

const api = useApi()
const route = useRoute()
const router = useRouter()
const currentTab: TabId = 'queue'
const siteStore = useSiteStore()

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

const { data: people, status: peopleStatus, error: peopleError } = await useAsyncData(() => api.rpcPersonList(), {
  server: false,
  lazy: false,
  default: () => [] as RpcPerson[]
})

const needsAssignmentTristate = ref<TristateValue>(TRISTATE_MIXED)
const hasExceptionTristate = ref<TristateValue>(TRISTATE_MIXED)
const selectedLabelFilters = ref<Record<number, TristateValue>>({})

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
    sortingFn: sortingFns.alphanumeric,
  }),
  columnHelper.accessor('rfcNumber', {
    header: 'RFC Number',
    cell: data => data.getValue(),
    sortingFn: sortingFns.alphanumeric,
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
    sortingFn: (rowA, rowB) => {
      const serializeRow = (row: typeof rowA) => row.original.labels?.map(label => label.slug).join('') ?? ''
      return serializeRow(rowA).localeCompare(serializeRow(rowB))
    },
  }),
  columnHelper.display({
      id: 'submitted',
      header: 'Submitted',
      cell: _data => '',
      sortingFn: sortingFns.alphanumeric,
  }),
  columnHelper.accessor(
    'externalDeadline',
    {
      header: 'Deadline',
      cell: data => {
        const value = data.getValue()
        return h('span', { class: 'text-xs' }, value ? DateTime.fromJSDate(value).toLocaleString(
          DateTime.DATE_MED_WITH_WEEKDAY
        ) : undefined)
      },
      sortingFn: (rowA, rowB) => sortDate(rowA.original.externalDeadline, rowB.original.externalDeadline),
    }
  ),
  columnHelper.accessor(
    'assignmentSet',
    {
      header: 'Assignees',
      cell: (data) => {
        const assignments = data.getValue()
        if (!assignments) {
          return 'No assignments'
        }

        const formattedValue: VNode[] = []
        const assignmentsByPerson = groupBy(
          assignments,
          (assignment) => assignment.person
        )

        const firstAssignment = assignments[0]
        for (const [personId, assignments] of Object.entries(assignmentsByPerson)) {
          const person = people.value.find(
            (p) => p.id === parseFloat(personId)
          )
          formattedValue.push(
            h(Anchor, {
              href: firstAssignment ? `/team/${firstAssignment.id}` : undefined
            }, () => [
              person ? person.name : pending ? `...` : '(unknown person)',
              ' ',
              ...assignments
                .sort((a, b) => a.role.localeCompare(b.role, 'en'))
                .map((assignment) => h(BaseBadge, { label: assignment.role }))
            ])
          )
        }

        return h('div', formattedValue)
      },
    }
  ),
  columnHelper.accessor(
    'actionholderSet',
    {
      header: 'Action Holders', cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h('span', {}, value ?
          value.map(actionHolder => actionHolder.body ?? actionHolder.name ?? 'No name')
          : undefined)
      },
      sortingFn: sortingFns.alphanumeric,
    }
  ),
  columnHelper.accessor(
    'pendingActivities',
    {
      header: 'Pending Activities', cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h('div', value.map(rpcRole => h(BaseBadge, { label: rpcRole.name })))
      },
    }
  ),
  columnHelper.accessor(
    'id',
    {
      header: 'Estimated Completion', cell: _data => '---',
      sortingFn: sortingFns.alphanumeric,
    }
  ),
  columnHelper.accessor(
    'pages',
    {
      header: 'Pages',
      cell: data => data.getValue(),
      sortingFn: sortingFns.alphanumeric,
      sortUndefined: 'last',
    }
  ),
  columnHelper.accessor(
    'cluster',
    {
      header: 'Cluster', cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h(Anchor, { href: `/clusters/${value.number}` }, () => [
          h(Icon, { name: 'pajamas:group', class: 'h-5 w-5 inline-block mr-1' }),
          value.number
        ])
      },
      sortingFn: (rowA, rowB, columnId) => {
        const a = rowA.getValue(columnId)?.number
        const b = rowB.getValue(columnId)?.number
        if (a == null && b == null) return 0
        if (a == null) return 1
        if (b == null) return -1
        return Number(a) - Number(b)
      },
      sortUndefined: 'last',
    }
  ),
]

const allLabelFilters = computed(() => {
  if (data.value === undefined) {
    return []
  }
  const allLabels = data.value.flatMap(
    (doc) => (doc && "labels" in doc ? doc.labels : []) as Label[]
  )
  const uniqueLabels = uniqBy(allLabels, label => label.id)
  const usedUniqueLabels = uniqueLabels.filter(label => {
    return label.used !== undefined ? label.used : true
  })
  return usedUniqueLabels
})


const table = useVueTable({
  get data() {
    return data.value
  },
  columns,
  state: {
    get globalFilter() {
      return JSON.stringify([
        needsAssignmentTristate.value,
        hasExceptionTristate.value,
        selectedLabelFilters.value,
        searchQuery.value
      ])
    },
    get sorting() {
      return sorting.value
    },
  },
  globalFilterFn: (row) => {
    const d = row.original
    if (d.disposition !== 'in_progress') {
      return false
    }

   // Search filter
   if (searchQuery.value && searchQuery.value.trim()) {
     const searchTerm = searchQuery.value.trim().toLowerCase()
     const nameMatch = d.name?.toLowerCase().includes(searchTerm)
     const rfcMatch = d.rfcNumber?.toString().toLowerCase().includes(searchTerm)
     if (!nameMatch && !rfcMatch) {
       return false
     }
   }

    const needsAssignmentFilterFn = () => {
      if (needsAssignmentTristate.value === true) {
        return Boolean(!d.assignmentSet || d.assignmentSet.length === 0)
      } else if (needsAssignmentTristate.value === false) {
        return Boolean(d.assignmentSet ? d.assignmentSet.length > 0 : false)
      } else if (needsAssignmentTristate.value === TRISTATE_MIXED) {
        return true
      }
    }

    const hasExceptionFilterFn = () => {
      const hasException = Boolean(d.labels?.filter((lbl: any) => lbl.isException).length)
      if (hasExceptionTristate.value === true) {
        return hasException
      } else if (hasExceptionTristate.value === false) {
        return !hasException
      } else if (hasExceptionTristate.value === TRISTATE_MIXED) {
        return true
      }
    }

    if (!(needsAssignmentFilterFn() && hasExceptionFilterFn())) {
      return false
    }

    const entries = Object.entries(selectedLabelFilters.value)
    if (!(entries.every(([labelIdStr, tristate]) => {
      const labelId = parseFloat(labelIdStr)
      switch (tristate) {
        case TRISTATE_MIXED:
          return true
        case true:
          return d.labels ? d.labels.some(label => label.id === labelId) : false
        case false:
          return d.labels ? !d.labels.some(label => label.id === labelId) : true
      }
    })
    )) {
      return false
    }

    return true
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

const searchQuery = computed({
  get: () => siteStore.search,
  set: (value: string) => { siteStore.search = value }
})

onMounted(() => {
  if (route.query.search && route.query.search !== siteStore.search) {
    siteStore.search = route.query.search as string
  }
})

watch(() => route.query.search, (newSearch) => {
  siteStore.search = newSearch as string || ''
})


watch(() => siteStore.search, (newSearch) => {
  const query = { ...route.query }
  if (newSearch) {
    query.search = newSearch
  } else {
    delete query.search
  }
  router.replace({ query })
})

</script>
