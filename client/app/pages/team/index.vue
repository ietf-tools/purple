<template>
  <div>
    <TitleBlock title="Manage Team Members"
      summary="A list of all the users having access to this tool.">
      <template #right>
        <RefreshButton :pending="pending" class="mr-3" @refresh="refresh" />
        <button v-if="userStore.isManager" type="button"
          class="flex items-center rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          @click="newTeamMember">
          <Icon name="uil:plus" class="-ml-1 h-5 w-5 mr-2" aria-hidden="true" />
          New Team Member
        </button>
      </template>
    </TitleBlock>

    <ErrorAlert v-if="error">
      {{ error }}
    </ErrorAlert>

    <h2 class="font-bold mt-5">Filters</h2>
    <div class="ml-1">
      <RpcCheckbox
        label="Only show active?"
        :value="true"
        :checked="isActiveFilter"
        @change="isActiveFilter = !isActiveFilter"
        size='medium'
        class="mr-3"
      />
    </div>

    <RpcTable class="mt-5">
      <RpcThead>
        <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <RpcTh v-for="header in headerGroup.headers" :key="header.id" :colSpan="header.colSpan"
            :is-sortable="header.column.getCanSort()" :sort-direction="header.column.getIsSorted()"
            @click="header.column.getToggleSortingHandler()?.($event)">
            <div class="flex items-center gap-2">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
              <Transition name="sort-indicator">
                <Icon v-if="header.column.getCanSort()" name="heroicons:arrows-up-down"
                  class="text-gray-400 opacity-60 hover:opacity-100" />
              </Transition>
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
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
  createColumnHelper,
  getFilteredRowModel,
  getSortedRowModel,
  type SortingState,
} from '@tanstack/vue-table'
import { UserCreateDialog } from '#components'
import { overlayModalKey } from '~/providers/providerKeys'
import type { RpcPerson } from '~/purple_client'
import Anchor from '~/components/Anchor.vue'
import BaseBadge from '~/components/BaseBadge.vue'

const _overlayModal = inject(overlayModalKey)
if (!_overlayModal) {
  throw Error('Expected injection of overlayModalKey')
}
const { openOverlayModal } = _overlayModal

useHead({
  title: 'Manage Team Members'
})

const userStore = useUserStore()

const api = useApi()

// METHODS

function newTeamMember() {
  openOverlayModal({
    component: UserCreateDialog,
    mode: 'side'
  })
}

// INIT

const { data: people, pending, status, error, refresh } = await useAsyncData(
  'team',
  () => {
    return api.rpcPersonList()
  },
  {
    default: () => [] as RpcPerson[],
    lazy: true,
    server: false,
  }
)

const columnHelper = createColumnHelper<RpcPerson>()

const columns = [
  columnHelper.accessor('name', {
    header: 'Document',
    cell: data => {
      return h(Anchor, { href: `/team/${data.row.original.id}`, 'class': ANCHOR_STYLE }, () => [
        data.getValue(),
        ` (#${data.row.original.id}${isActiveFilter.value === false ? `, ${data.row.original.isActive ? 'active' : 'inactive' }` : ''})`
      ])
    },
    sortingFn: 'alphanumeric',
  }),
  columnHelper.accessor(
    'roles', {
    header: 'Roles',
    cell: data => {
      const roles = data.getValue()
      return h('ul', { class: ''}, roles.map(
        role => h('li', { class: ''}, [
          h(BaseBadge, { label: role.slug, class: 'mr-1' }),
          JSON.stringify(role)
        ])
      ))
    },
    enableSorting: false,
  }),
  columnHelper.accessor(
    'capabilities', {
    header: 'Capabilities',
    cell: data => {
      const capabilities = data.getValue()
      return h('ul', { class: ''}, capabilities.map(
        capability => h('li', { class: ''}, [
          JSON.stringify(capability)
        ])
      ))
    },
    sortingFn: 'alphanumeric',
  })
]

const sorting = ref<SortingState>([])

const isActiveFilter = ref(true)

const table = useVueTable({
  get data() {
    return people.value
  },
  columns,
  state: {
    get globalFilter() {
      return JSON.stringify([
        isActiveFilter.value
      ])
    },
    get sorting() {
      return sorting.value
    },
  },
  enableFilters: true,
  globalFilterFn: (row) => {
    if (isActiveFilter.value) {
      return row.original.isActive === isActiveFilter.value
    }
    return true
  },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  onSortingChange: updaterOrValue => {
    sorting.value =
      typeof updaterOrValue === 'function'
        ? updaterOrValue(sorting.value) : updaterOrValue
  }
})

</script>
