<template>
  <div>
    <TitleBlock title="Queue" summary="Where the magic happens.">
      <template #right>
        <div
          class="mt-2 text-right text-gray-700 dark:text-neutral-400 sm:ml-16 sm:mt-0"
        >
          <div class="text-sm">
            Backlog
            <strong class="text-rose-700"
              >larger
              <Icon name="uil:angle-double-up" class="text-lg -mt-0.5" />
            </strong>
            than a week ago
          </div>
          <div class="text-xs">
            <strong>2 weeks</strong> to drain the queue
            <em>(was <strong>3 days</strong> a week ago)</em>
          </div>
        </div>
      </template>
    </TitleBlock>

    <!-- TABS -->

    <div class="flex justify-center items-center">
      <TabNav :tabs="tabs" :selected="currentTab" />
      <RefreshButton :pending="pending" class="ml-3" @refresh="refresh" />
      <button type="button" class="btn-secondary ml-3" @click.stop>
        <span class="sr-only">Filter</span>
        <Icon
          name="solar:filter-line-duotone"
          size="1.5em"
          class="text-gray-500 dark:text-neutral-300"
          aria-hidden="true"
        />
      </button>
    </div>

    <div v-if="currentTab=== 'queue'">
      <div class="flex flex-row gap-x-8 justify-between mb-4">
        <fieldset>
          <legend class="font-bold text-base">
            Filters
            <span class="text-md">&nbsp;</span>
          </legend>
          <div class="flex flex-col gap-1">
            <RpcTristateButton
              :checked="needsAssignmentTristate"
              @change="(tristate) => needsAssignmentTristate = tristate"
            >
              Needs Assignment?
            </RpcTristateButton>
            <RpcTristateButton
              :checked="hasExceptionTristate"
              @change="(tristate) => hasExceptionTristate = tristate"
            >
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
            <LabelsFilter
              v-model:all-label-filters="allLabelFilters"
              v-model:selected-label-filters="selectedLabelFilters"
            />
          </div>
        </fieldset>
      </div>
    </div>

    <!-- DATA TABLE -->

    <div class="mt-2 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <div
            class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg"
          >
            <DocumentTable
              :columns="columns"
              :data="filteredDocuments"
              row-key="id"
              :loading="pending"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import Fuse from 'fuse.js/basic'
import { groupBy, uniqBy } from 'lodash-es'
import { useSiteStore } from '@/stores/site'
import Badge from '../../components/BaseBadge.vue'
import { TRISTATE_MIXED } from '~/utilities/tristate'
import type { TristateValue } from '~/utilities/tristate'
import type { Column, Row } from '~/components/DocumentTableTypes'
import type { ActionHolder, Assignment, Label, QueueItem, SubmissionListItem } from '~/purple_client'
import type { Tab } from '~/components/TabNavTypes'

// ROUTING

const route = useRoute()

// STORES

const siteStore = useSiteStore()

// DIALOGS

const snackbar = useSnackbar()

// API

const api = useApi()

// DATA

const tabs = [
  {
    id: 'submissions',
    name: 'Submissions',
    to: '/queue/submissions',
    icon: 'uil:bolt-alt'
  },
  {
    id: 'enqueuing',
    name: 'Enqueuing',
    to: '/queue/enqueuing',
    icon: 'ic:outline-queue'
  },
  {
    id: 'queue',
    name: 'Queue',
    to: '/queue/queue',
    icon: 'uil:clock'
  },
  {
    id: 'published',
    name: 'Recently Published',
    to: '/queue/published',
    icon: 'uil:check-circle'
  }
] as const satisfies Tab[]

type TabId = (typeof tabs)[number]["id"]

const needsAssignmentTristate = ref<TristateValue>(TRISTATE_MIXED)
const hasExceptionTristate = ref<TristateValue>(TRISTATE_MIXED)

// COMPUTED

const deadlineCol = {
  key: 'deadline',
  label: 'Deadline',
  field: 'externalDeadline',
  format: (val: any) =>
    val
      ? DateTime.fromJSDate(val as Date).toLocaleString(
          DateTime.DATE_MED_WITH_WEEKDAY
        )
      : '',
  classes: 'text-xs'
}

const { data: people } = await useAsyncData(() => api.rpcPersonList(), {
  server: false,
  default: () => []
})

const getDocLink = (tab: string, row: Row) => {
  switch (tab) {
    case 'submissions':
      return `/docs/import/?documentId=${row.id}`
    case 'enqueuing':
      return `/docs/${row.name}/enqueue`
    default:
      return `/docs/${row.name}`
  }
}

const columns = computed(() => {
  const cols: Column[] = [
    {
      key: 'name',
      label: 'Document',
      field: 'name',
      classes: 'text-sm font-medium',
      link: (row: Row) => getDocLink(currentTab.value, row)
    },
    {
      key: 'labels',
      label: 'Labels',
      labels: (row) => (row.labels || []) as string[]
    }
  ]
  const tabsWithSubmitted = ['submissions', 'enqueuing', 'queue'] satisfies TabId[]

  if (
    (tabsWithSubmitted as TabId[]).includes(currentTab.value)
  ) {
    cols.push({
      key: 'submitted',
      label: 'Submitted',
      field: 'submitted',
      format: (val) =>
        val
          ? DateTime.fromJSDate(val as Date).toLocaleString(
              DateTime.DATE_MED_WITH_WEEKDAY
            )
          : '',
      classes: 'text-xs'
    })
  }
  if (currentTab.value === 'queue') {
    cols.push(deadlineCol)
  }
  if (currentTab.value === 'published') {
    cols.unshift({
      key: 'rfc',
      label: 'RFC',
      field: 'rfc',
      format: (val: any) => `RFC ${val}`
    })
  }
  if (currentTab.value === 'queue') {
    cols.push({
      key: 'exception',
      label: 'Exception',
      field: 'exception',
      classes: 'text-rose-600 dark:text-rose-500'
    })
  }
  if ((currentTab.value === 'queue')) {
    cols.push({
      key: 'assignmentSet',
      label: 'Assignee (should allow multiple)',
      field: 'assignmentSet',
      formatType: 'all',
      format: (val) => {
        if (!val) {
          return 'No assignments'
        }
        const assignments = val as Assignment[]
        const formattedValue: VNode[] = []
        const assignmentsByPerson = groupBy(
          assignments,
          (assignment) => assignment.person
        )
        for (const [personId, assignments] of Object.entries(assignmentsByPerson)) {
          const person = people.value.find(
            (p) => p.id === parseFloat(personId)
          )
          formattedValue.push(
            h('span', [
              person ? person.name : '(unknown person)',
              ' ',
              ...assignments
                .sort((a, b) => a.role.localeCompare(b.role, 'en'))
                .map((assignment) => h(Badge, { label: assignment.role }))
            ])
          )
        }

        return formattedValue
      },
      link: (row: any) => (row.assignee ? `/team/${row.assignee.id}` : '')
    })
    cols.push(
      ...[
        {
          key: 'holder',
          label: 'Action Holder (should allow multiple)',
          field: 'holder',
          format: (val: any) => {
            const actionHolder = val as ActionHolder | undefined
            return actionHolder && 'body' in actionHolder ? String(actionHolder.body) : actionHolder?.name ?? 'No name'
          },
        },
        deadlineCol
      ]
    )
  }
  if (currentTab.value === 'queue') {
    cols.push(
      ...[
        {
          key: 'pendingActivities',
          label: 'Pending Activities',
          field: 'pendingActivities',
          format: (val: any) => {
            return h(Badge, { label: val.name })
          }
        },
        {
          key: 'estimatedCompletion',
          label: 'Estimated Completion',
          field: 'estimatedCompletion',
          format: (val: any) => {
            const dt = DateTime.fromISO(val)
            return dt.isValid
              ? dt.toLocaleString(DateTime.DATE_MED_WITH_WEEKDAY)
              : '---'
          },
          classes: 'text-xs'
        },
        {
          key: 'status',
          label: 'Status',
          field: 'status',
          classes: (val: any) =>
            val === 'overdue'
              ? 'font-medium text-rose-600 dark:text-rose-500'
              : 'text-emerald-600 dark:text-emerald-500'
        }
      ]
    )
  }
  if (currentTab.value === 'queue') {
    cols.push({
      key: 'cluster',
      label: 'Cluster',
      field: 'cluster',
      format: (value: any) => value?.number,
      icon: 'pajamas:group',
      link: (val: any) => (val.cluster ? `/clusters/${val.cluster.number}` : '')
    })
  }
  if (currentTab.value === 'published') {
    cols.push(
      ...[
        {
          key: 'owner',
          label: 'PUB Owner',
          field: 'owner',
          format: (val: any) => val?.name || 'Unknown',
          link: (row: any) => `/team/${row.holder?.id}`
        },
        {
          key: 'published',
          label: 'Published',
          field: 'published',
          format: (val: any) =>
            DateTime.fromISO(val).toLocaleString(
              DateTime.DATE_MED_WITH_WEEKDAY
            ),
          classes: 'text-xs'
        }
      ]
    )
  }
  return cols
})

const currentTab = computed((): TabId  => {
  const tab = route.params.section.toString() || 'submissions'
  console.log(`setting currentTab = ${tab}`)
  return tab as TabId
})

const filteredDocuments = computed(() => {
  if (!documents.value) return []

  let docs = []

  // -> Filter based on selected tab
  switch (currentTab.value) {
    case 'submissions':
      console.log('submissions', documents.value)

      docs = documents.value
      break
    case 'enqueuing':
      docs = documents.value.filter((d: any) => d.disposition === 'created')
      break
    case 'queue':
      docs = documents.value
        .filter(
          (d) => {
            return Boolean(d && 'disposition' in d ? d.disposition === 'in_progress' : true)
        })
        .filter(
          (d: any) => {
            const needsAssignmentFilterFn = () => {
              if(needsAssignmentTristate.value === true) {
                return Boolean(!d.assignmentSet || d.assignmentSet.length === 0)
              } else if(needsAssignmentTristate.value === false) {
                return Boolean(d.assignmentSet?.length > 0)
              } else if(needsAssignmentTristate.value === TRISTATE_MIXED) {
                return true
              }
            }

            const hasExceptionFilterFn = () => {
              const hasException = Boolean(d.labels?.filter((lbl: any) => lbl.isException).length)
              if(hasExceptionTristate.value === true) {
                return hasException
              } else if(hasExceptionTristate.value === false) {
                return !hasException
              } else if(hasExceptionTristate.value === TRISTATE_MIXED) {
                return true
              }
            }

            return needsAssignmentFilterFn() && hasExceptionFilterFn()
        })
        .filter(d => {
          if(!('labels' in d)) return true
          const entries = Object.entries(selectedLabelFilters.value)
          return entries.every(([labelIdStr, tristate]) => {
            const labelId = parseFloat(labelIdStr)
            switch(tristate) {
              case TRISTATE_MIXED:
                return true
              case true:
                return d.labels ? d.labels.some(label => label.id === labelId) : false
              case false:
                return d.labels ? !d.labels.some(label => label.id === labelId) : true
            }
          })
        })
        .map((d: any) => ({
          ...d,
          pendingActivities: d.pendingActivities,
          assignee: d.assignmentSet[0],
          holder: d.actionholderSet
        }))

      break
    default:
      docs = []
      break
  }

  // -> Fuzzy search
  if (siteStore.search) {
    const fuse = new Fuse(docs, {
      keys: ['name', 'rfc']
    })
    return fuse.search(siteStore.search).map((n) => n.item)
  } else {
    return docs
  }
})

// INIT

const {
  data: documents,
  pending,
  refresh
} = await useAsyncData(
  () => `queue-${currentTab.value}`,
  async () => {
    console.log(`currentTab.value = ${currentTab.value}`)
    try {
      if (currentTab.value === 'submissions') {
        return await api.submissionsList()
      } else {
        return await api.queueList()
      }
    } catch (err) {
      snackbar.add({
        type: 'error',
        title: 'Fetch Failed',
        text: String(err)
      })
    }
  },
  {
    server: false,
    lazy: true,
    default: () => []
  }
)

const allLabelFilters = computed(() => {
  if (documents.value === undefined) {
    return []
  }
  const allLabels = documents.value.flatMap(
    (doc) => (doc && "labels" in doc ? doc.labels : []) as Label[]
  )
  const uniqueLabels = uniqBy(allLabels, label => label.id)
  const usedUniqueLabels = uniqueLabels.filter(label => {
    return label.used !== undefined ? label.used : true
  })
  return usedUniqueLabels
})

const selectedLabelFilters = ref<Record<number, TristateValue>>({})

onMounted(() => {
  siteStore.search = ''
})
</script>
