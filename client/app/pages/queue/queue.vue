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
              :title="header.column.getCanSort() ? 'Click to sort' : ''"
            >
              <div class="flex items-center gap-2">
                <FlexRender
                  v-if="!header.isPlaceholder"
                  :render="header.column.columnDef.header"
                  :props="header.getContext()"
                />
                <Transition name="sort-indicator">
                  <Icon
                    v-if="header.column.getCanSort()"
                    name="heroicons:arrows-up-down"
                    class="text-gray-400 opacity-60 hover:opacity-100"
                  />
                </Transition>
              </div>
            </RpcTh>
          </tr>
        </RpcThead>
        <RpcTbody>
          <RpcRowMessage :status="[status, peopleStatus]" :column-count="table.getAllColumns().length"
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
  </div>

</template>

<script setup lang="ts">
import { Anchor, Icon, BaseBadge, BaseButton, RpcLabel, AssignmentModal } from '#components'
import { DateTime } from 'luxon'
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'
import { groupBy, uniqBy } from 'lodash-es'
import type { Assignment, Cluster, Label, QueueItem, RpcPerson, RpcRole } from '~/purple_client'
import { sortDate, sortLabels } from '~/utils/queue'
import type { TabId, AssignmentMessageProps } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'
import { useSiteStore } from '@/stores/site'
import { overlayModalKey } from '~/providers/providerKeys'

const api = useApi()

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
  lazy: true,
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
    'submittedAt',
    {
      header: 'Submitted (Weeks in queue)',
      cell: data => {
        const value = data.getValue()

        const submittedDate = DateTime.fromJSDate(value)
        const now = DateTime.now()
        const diffInDays = now.diff(submittedDate, 'days').days
        const weeksInQueue = Math.floor(diffInDays / 7 * 2) / 2 // Floor to nearest 0.5

        return h(
          'div',
          { class: 'text-xs' },
          value ? [
            h('div', submittedDate.toISODate()),
            h('div', `(${weeksInQueue} week${weeksInQueue !== 1 ? 's' : ''})`)
          ] : []
        )
      },
      sortingFn: (rowA, rowB, columnId) => {
        const a = rowA.getValue(columnId)
        const b = rowB.getValue(columnId)
        return (a > b) ? 1 : (a < b) ? -1 : 0
      },
    }
  ),
  columnHelper.accessor(
    'externalDeadline',
    {
      header: 'Deadline',
      cell: data => {
        const value = data.getValue()
        return h(
          'span',
          { class: 'text-xs' },
          [value ? DateTime.fromJSDate(value).toISODate() : '']
        )
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

        const rfcToBeId = data.row.original.id
        if (rfcToBeId === undefined) {
          throw Error(`Internal error: expected queueItem to have id but was ${JSON.stringify(data.row.original)}`)
        }

        const listItems: VNode[] = []

        const assignmentsByRole = groupBy(
          assignments,
          (assignment) => assignment.role
        )

        const orderedRole = Object.keys(assignmentsByRole)
          .sort((a, b) => a.localeCompare(b, 'en'))

        for (const role of orderedRole) {
          const assignments = assignmentsByRole[role] ?? []

          listItems.push(h('li', {}, [
            h(BaseBadge, { label: role, class: 'mr-1' }),
            ...assignments.map(assignment => {
              const rpcPerson = people.value.find((p) => p.id === assignment.person)
              return h(Anchor, {
                href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
                class: [ANCHOR_STYLE, 'text-sm nowrap']
              }, () => [
                rpcPerson ? rpcPerson.name : pending ? `...` : '(unknown person)',
              ])
            }).reduce((acc, item, index, arr) => {
              acc.push(item)
              if (index < arr.length - 1) {
                acc.push(', ')
              } else {
                acc.push(' ')
              }
              return acc
            }, [] as (VNode | string)[]),
            h(BaseButton, { btnType: 'outline', size: 'xs', 'onClick': () => openAssignmentModal({ type: 'change', assignments, role, rfcToBeId }) }, () => 'Change'),
          ]))
        }

        return h('ul', {}, listItems)
      },
      enableSorting: false,
    }
  ),
  columnHelper.accessor(
    'actionholderSet',
    {
      header: 'Action Holders',
      cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h('span', {}, value.map(actionHolder => actionHolder.body ?? actionHolder.name ?? 'No name'))
      },
      sortingFn: 'alphanumeric',
    }
  ),
  columnHelper.accessor(
    'pendingActivities',
    {
      header: 'Pending Activities',
      cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }

        const rfcToBeId = data.row.original.id
        if (rfcToBeId === undefined) {
          throw Error(`Internal error: expected queueItem to have id but was ${JSON.stringify(data.row.original)}`)
        }

        return h('ul', {}, value.map(rpcRole =>
          h('li', {}, [
            h(BaseBadge, { label: rpcRole.name }),
            h(BaseButton, { btnType: 'outline', size: 'xs', 'onClick': () => openAssignmentModal({ type: "assign", role: rpcRole.slug, rfcToBeId }) }, () => 'Assign'),
          ])
        ))
      },
      enableSorting: false,
    }
  ),
  columnHelper.accessor(
    'pages',
    {
      header: 'Status',
      cell: _data => '',
      sortingFn: 'alphanumeric',
    }
  ),
  columnHelper.accessor(
    'cluster',
    {
      header: 'Cluster',
      cell: data => {
        const value = data.getValue()
        if (!value) {
          return undefined
        }
        return h(Anchor, { href: `/clusters/${value.number}` }, () => [
          h(Icon, { name: 'pajamas:group', class: 'h-5 w-5 inline-block mr-1' }),
          String(value.number)
        ])
      },
      sortingFn: (rowA, rowB) => sortCluster(rowA.original.cluster, rowB.original.cluster),
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

const { data: clusters, refresh: refreshClusters, status: clustersStatus, error: clustersError } = await useAsyncData(() => api.clustersList(), {
  server: false,
  lazy: false,
  default: () => [] as Cluster[]
})

const snackbar = useSnackbar()
const overlayModal = inject(overlayModalKey)

const openAssignmentModal = (assignmentMessage: AssignmentMessageProps) => {
  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal, closeOverlayModal } = overlayModal

  if (peopleStatus.value === 'error') {
    snackbar.add({
      type: 'error',
      title: 'Error loading people. Reload page.',
      text: `Error: ${peopleError}`
    })
    return
  }

  if (clustersStatus.value === 'error') {
    snackbar.add({
      type: 'error',
      title: 'Error loading clusters. Reload page.',
      text: `Error: ${clustersError}`
    })
    return
  }

  if (clustersStatus.value !== 'success') {
    snackbar.add({
      type: 'warning',
      title: 'Loading clusters',
      text: 'Please wait...'
    })
    return
  }

  if (peopleStatus.value !== 'success') {
    snackbar.add({
      type: 'warning',
      title: 'Loading people',
      text: 'Please wait...'
    })
    return
  }

  // Calculate the workload of an editor
  const peopleWorkload: Record<number, RpcPersonWorkload> = {}
  const addToPersonWorkload = (personId: number | null | undefined, clusterIds: number[], role: Assignment['role'], pageCount: number | undefined): void => {
    assertIsNumber(personId)
    assert(role.length !== 0)
    assert(typeof pageCount === 'number')

    const editorWorkload: RpcPersonWorkload = peopleWorkload[personId] ?? { personId, clusterIds: [], pageCountByRole: {} }
    if (clusterIds !== undefined) {
      clusterIds.forEach(clusterId => {
        if (!editorWorkload.clusterIds.includes(clusterId)) {
          editorWorkload.clusterIds.push(clusterId)
        }
      })
    }
    editorWorkload.pageCountByRole[role] = (editorWorkload.pageCountByRole[role] ?? 0) + pageCount

    peopleWorkload[personId] = editorWorkload
  }
  data.value.forEach(doc => {
    const clustersWithDocument = clusters.value.filter(cluster => cluster.documents.some(clusterDocument =>
      clusterDocument.name === doc.name
    ))
    const clusterIds = clustersWithDocument.map(cluster => cluster.number)
    doc.assignmentSet?.forEach(assignment => {
      addToPersonWorkload(assignment.person, clusterIds, assignment.role, doc.pages)
    })
  })

  openOverlayModal({
    component: AssignmentModal,
    componentProps: {
      message: assignmentMessage,
      people: people.value,
      clusters: clusters.value,
      peopleWorkload,
      onSuccess: () => {
        refresh()
        refreshClusters()
      }
    },
  })
}

</script>
