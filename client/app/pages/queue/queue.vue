<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
    </TitleBlock>

    <QueueTabs :current-tab="currentTab" />

    <ErrorAlert v-if="error || peopleError">
      {{ error }} {{ peopleError }}
    </ErrorAlert>

    <div class="flex flex-row gap-x-8 justify-between mb-4 text-gray-800 dark:text-gray-300">
      <fieldset>
        <legend class="font-bold text-sm flex">
          Filters
          <span class="text-md">&nbsp;</span>
        </legend>
        <div class="flex flex-col gap-1 pt-1">
          <RpcTristateButton :checked="needsAssignmentTristate"
            @change="(tristate: TristateValue) => needsAssignmentTristate = tristate">
            Needs Assignment?
          </RpcTristateButton>
          <RpcTristateButton :checked="hasExceptionTristate"
            @change="(tristate: TristateValue) => hasExceptionTristate = tristate">
            Has Exception?
          </RpcTristateButton>
          <RpcTristateButton :checked="isBlockedTristate"
            @change="(tristate: TristateValue) => isBlockedTristate = tristate">
            Is Blocked?
          </RpcTristateButton>
        </div>
      </fieldset>
      <div class="w-64 flex flex-col gap-4">
        <fieldset>
          <legend class="font-bold text-sm flex items-end">
            Current Assignment Role
            <span class="text-md">&nbsp;</span>
          </legend>
            <div class="flex flex-col pt-1">
              <select
                v-model="selectedRoleFilter"
                class="px-3 py-1 border border-gray-300 text-gray-800 dark:text-gray-200 rounded-md text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="null">All Roles</option>
                <option v-for="role in allRoles" :key="role" :value="role">
                  {{ role }}
                </option>
              </select>
            </div>
        </fieldset>
        <fieldset>
          <legend class="font-bold text-sm flex items-end">
            Pending Assignment Role
            <span class="text-md">&nbsp;</span>
          </legend>
            <div class="flex flex-col pt-1">
              <select
                v-model="selectedPendingRoleFilter"
                class="px-3 py-1 border border-gray-300 text-gray-800 dark:text-gray-200 rounded-md text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option :value="null">All Roles</option>
                <option v-for="role in allPendingRoles" :key="role" :value="role">
                  {{ role }}
                </option>
              </select>
            </div>
        </fieldset>
      </div>
      <fieldset class="flex-1">
        <legend class="font-bold text-sm flex items-end">
          Label
          <span class="text-md">&nbsp;</span>
        </legend>
        <div class="grid grid-cols-[repeat(auto-fill,11em)] gap-x-3 pt-1">
          <LabelsFilter v-model:all-label-filters="allLabelFilters"
            v-model:selected-label-filters="selectedLabelFilters" />
        </div>
      </fieldset>
    </div>

    <RpcTable>
      <RpcThead>
        <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
            :is-sortable="header.column.getCanSort()" :sort-direction="header.column.getIsSorted()"
            @click="header.column.getToggleSortingHandler()?.($event)"
            :title="header.column.getCanSort() ? 'Click to sort' : ''">
            <div class="flex items-center gap-2">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
            </div>
          </RpcTh>
        </tr>
      </RpcThead>
      <RpcTbody>
        <RpcRowMessage :status="[status, clustersStatus, peopleStatus]" :column-count="table.getAllColumns().length"
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
import type { Assignment, Cluster, Label, QueueItem, RpcPerson } from '~/purple_client'
import { calculatePeopleWorkload } from '~/utils/queue'
import type { QueueTabId, AssignmentMessageProps } from '~/utils/queue'
import { ANCHOR_STYLE } from '~/utils/html'
import { useSiteStore } from '@/stores/site'
import { overlayModalKey } from '~/providers/providerKeys'

const api = useApi()
const currentTab: QueueTabId = 'queue'
const route = useRoute()
const router = useRouter()
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
const isBlockedTristate = ref<TristateValue>(TRISTATE_MIXED)
const selectedLabelFilters = ref<Record<number, TristateValue>>({})
const selectedRoleFilter = ref<string | null>(null)

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
    'enqueuedAt',
    {
      header: () => h('div', { class: 'text-center' }, [
        h('div', 'Enqueue Date'),
        h('div', '(Weeks in queue)')
      ]),
      cell: data => {
        const value = data.getValue()
        if(!value) return ''

        const enqueuedAt = DateTime.fromJSDate(value)
        const now = DateTime.now()
        const diffInDays = now.diff(enqueuedAt, 'days').days
        const weeksInQueue = Math.floor(diffInDays / 7 * 2) / 2 // Floor to nearest 0.5

        return h(
          'div',
          { class: 'text-xs' },
          value ? [
            h('div', enqueuedAt.toISODate() ?? ''),
            h('div', `(${weeksInQueue} week${weeksInQueue !== 1 ? 's' : ''})`)
          ] : []
        )
      },
      sortingFn: (rowA, rowB, columnId) => {
        const now = DateTime.now()

        const a = rowA.getValue(columnId)
        if (!(a instanceof Date)) {
          console.error("Not date was", a)
          throw Error(`Expected date but was something else. See console.`)
        }
        const aDateTime = DateTime.fromJSDate(a)
        const aDiffInDays = now.diff(aDateTime, 'days').days

        const b = rowB.getValue(columnId)
        if (!(b instanceof Date)) {
          console.error("Not date was", b)
          throw Error(`Expected date but was something else. See console.`)
        }
        const bDateTime = DateTime.fromJSDate(b)
        const bDiffInDays = now.diff(bDateTime, 'days').days

        return (aDiffInDays > bDiffInDays) ? 1 : (aDiffInDays < bDiffInDays) ? -1 : 0
      },
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

        const assignmentsByRoles = groupBy(
          assignments,
          (assignment) => assignment.role
        )

        const orderedRoles = Object.keys(assignmentsByRoles)
          .sort((a, b) => a.localeCompare(b, 'en'))

        for (const role of orderedRoles) {
          const assignmentsOfRole = assignmentsByRoles[role] ?? []

          const redundantAssignmentsOfSamePersonToSameRole = assignmentsOfRole.filter((assignment, _index, arr) => {
            const { person } = assignment
            if (person === undefined || person == null) {
              return false
            }
            const firstAssignmentOfPersonToRole = arr.find(arrAssignment => assignment.person && arrAssignment.person && arrAssignment.person === assignment.person)
            if (!firstAssignmentOfPersonToRole) {
              console.log(`Couldn't find first assignment for person #${assignment.person} in`, arr)
              throw Error(`Internal error. Should be able to find first assignment for person #${assignment.person}. See console`)
            }
            // the first assignment of person in the list of assignments should always match the current assignment of person
            // because there shouldn't be duplicate/redundant assignments
            // but if the id is different then it is a redundant assignment,
            // so we'll prompt the user to delete them
            return assignment.id !== firstAssignmentOfPersonToRole.id
          })

          listItems.push(h('li', { class: 'flex gap-3' }, [
            h('span',
              h(BaseBadge, { label: role, class: 'mr-1' })),
            h('ul', { class: 'flex flex-col gap-2' }, [
              ...assignmentsOfRole.map(assignment => {
                const rpcPerson = people.value.find((p) => p.id === assignment.person)
                return h(Anchor, {
                  href: rpcPerson ? `/team/${rpcPerson.id}` : undefined,
                  class: [ANCHOR_STYLE, 'text-sm nowrap']
                }, () => [
                  rpcPerson ? rpcPerson.name : pending ? `...` : '(unknown person)',
                ])
              }).reduce((acc, item, index, arr) => {
                // add commas between items
                const listItemChildren = []
                listItemChildren.push(item)
                if (index < arr.length - 1) {
                  listItemChildren.push(', ')
                } else {
                  listItemChildren.push(' ')
                }
                const listItem = h('li', listItemChildren)
                acc.push(listItem)
                return acc
              }, [] as (VNode | string)[])]),
            h('span', [
              h(BaseButton, { btnType: 'outline', size: 'xs', 'onClick': () => openAssignmentModal({ type: 'change', assignments: assignmentsOfRole, role, rfcToBeId }) }, () => 'Change'),
              ...redundantAssignmentsOfSamePersonToSameRole.map(redundantAssignment => {
                return h(BaseButton, { btnType: 'delete', size: 'xs', 'onClick': () => deleteRedundantAssignment(redundantAssignment) }, () => `Delete redundant assignment of ${getPersonNameById(redundantAssignment.person)}`)
              })])
          ]))
        }

        return h('ul', { class: 'flex flex-col gap-x-1 gap-y-3' }, listItems)
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

        return h('ul', { class: 'flex flex-col gap-3' }, value.map(rpcRole =>
          h('li', { class: 'flex flex-row gap-2' }, [
            h('div', h(BaseBadge, { label: rpcRole.slug })),
            h('div', h(BaseButton, { btnType: 'outline', size: 'xs', 'onClick': () => openAssignmentModal({ type: "assign", role: rpcRole.slug, rfcToBeId }) }, () => 'Assign')),
          ])
        ))
      },
      enableSorting: false,
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

const allRoles = computed(() => {
  if (data.value === undefined) {
    return []
  }
  const roles = data.value.flatMap(
    (doc) => doc.assignmentSet?.map(assignment => assignment.role) || []
  )
  return [...new Set(roles)].sort()
})

const allPendingRoles = computed(() => {
  if (data.value === undefined) {
    return []
  }
  const roleSlugs = data.value.flatMap(
    (doc) => doc.pendingActivities?.map(role => role.slug) || []
  )
  return [...new Set(roleSlugs)].sort()
})

const selectedPendingRoleFilter = ref(null)

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
        isBlockedTristate.value,
        selectedLabelFilters.value,
        selectedRoleFilter.value,
        selectedPendingRoleFilter.value,
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

    if (selectedRoleFilter.value) {
      const hasRole = d.assignmentSet?.some(assignment => assignment.role === selectedRoleFilter.value)
      if (!hasRole) {
        return false
      }
    }

    if (selectedPendingRoleFilter.value) {
      const hasRole = d.pendingActivities?.some(role => role.slug === selectedPendingRoleFilter.value)
      if (!hasRole) {
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

    const isBlockedFilterFn = () => {
      if (isBlockedTristate.value === true) {
        return Boolean(d.assignmentSet ? d.assignmentSet.filter(a => a.role === 'blocked').length > 0 : false)
      } else if (isBlockedTristate.value === false) {
        return Boolean(d.assignmentSet ? d.assignmentSet.filter(a => a.role === 'blocked').length === 0 : true)
      } else if (isBlockedTristate.value == TRISTATE_MIXED) {
        return true
      }
    }

    if (!(needsAssignmentFilterFn() && hasExceptionFilterFn() && isBlockedFilterFn())) {
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

const { data: clusters, refresh: refreshClusters, status: clustersStatus, error: clustersError } = await useAsyncData(
  'queue2-clusterslist',
  () => api.clustersList(),
  {
    server: false,
    lazy: false,
    default: () => [] as Cluster[]
  }
)

const reloadTableAfterAssignmentChange = () => {
  refresh()
  refreshClusters()
}

const getPersonNameById = (personId?: number | null): string => {
  if (personId === undefined || personId === null) return 'Unknown'
  const person = people.value.find(person => person.id === personId)
  return person?.name ?? 'Unknown'
}

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

  const peopleWorkload = calculatePeopleWorkload(clusters.value, data.value)

  openOverlayModal({
    component: AssignmentModal,
    componentProps: {
      message: assignmentMessage,
      people: people.value,
      clusters: clusters.value,
      peopleWorkload,
      onSuccess: reloadTableAfterAssignmentChange
    },
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
      console.info("Modal has closed", { e })
    } else {
      console.error(e)
      throw e
    }
  })
}

const deleteRedundantAssignment = async (redundantAssignment: Assignment) => {
  const { id, person, role } = redundantAssignment
  if (id === undefined || id === null) {
    snackbar.add({
      type: 'error',
      title: "Can't delete redundant assignment without an id",
      text: `typeof id = ${typeof id}`
    })
    return
  }
  if (person === undefined || person === null) {
    snackbar.add({
      type: 'error',
      title: "Can't delete redundant assignment without an person",
      text: `typeof person = ${typeof person}`
    })
    return
  }
  try {
    await api.assignmentsDestroy({ id })
    reloadTableAfterAssignmentChange()
    snackbar.add({
      type: 'success',
      title: "Successfully deleted redundant assignment. Reloading...",
      text: `${getPersonNameById(person)} had multiple assignments to role ${JSON.stringify(role)}`
    })
  } catch (e) {
    reloadTableAfterAssignmentChange() // although there was an error it's possible a db change occurred so we should resync
    console.error('Deleting redundant assignment error:', e, redundantAssignment)
    snackbar.add({
      type: 'error',
      title: "Can't delete redundant assignment. See console for details.",
      text: `Error: ${JSON.stringify(e).substring(0, 100)}`
    })
  }
}

useHead({
  title: 'RPC Queue'
})
</script>
