<template>
  <div>
    <TitleBlock title="Cluster Management">
      <template #right>
        <RefreshButton :pending="pending" class="mr-3" @refresh="refresh" />
        <button type="button"
          class="flex items-center rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          @click="state.createDialogShown = true">
          <Icon name="uil:plus" class="-ml-1 h-5 w-5 mr-2" aria-hidden="true" />
          New Cluster
        </button>
      </template>
    </TitleBlock>

    <form class="flex flex-row items-center w-[200px] pt-5">
      <label class="text-gray-900 text-sm font-bold mr-1" for="filterInput">Filter:</label>
      <input type="text" inputmode="numeric" pattern="[0-9]*" id="filterInput" v-model="filterValueString"
        class="focus:shadow-gray-300 inline-flex w-full flex-1 items-center justify-center rounded-lg px-3 text-sm leading-none outline-none border-gray-500 text-gray-900"
        placeholder="E.g. 20" />
    </form>

    <div class="flex flex-col gap-3 mt-5 mb-10">
      <div v-for="cluster in filteredClusters" :key="cluster.number"
        class="flex flex-row items-start border border-gray-300 shadow-md rounded-md px-2 py-1">
        <h2 class="flex flex-row items-start text-lg whitespace-nowrap grow-0 shrink-0 w-[7em] px-2">
          <a :href="`/clusters/${cluster.number}/`" :class="ANCHOR_STYLE">
            Cluster {{ cluster.number }}
          </a>
        </h2>
        <ul class="flex flex-wrap pt-1 gap-y-1 gap-x-3 text-xs leading-[1]">
          <DocumentCardMini v-for="document in cluster.documents" :document="document" />
        </ul>
      </div>
    </div>

    <!--    <UserCreateDialog v-model:isShown="state.createDialogShown"/>-->
  </div>
</template>

<script setup lang="ts">
import RefreshButton from '~/components/RefreshButton.vue'

useHead({
  title: 'Manage Clusters'
})

const state = reactive({
  selectedClusterNumber: '',
  createDialogShown: false,
  notifDialogShown: false,
  notifDialogMessage: ''
})

const filterValueString = ref('')

const api = useApi()

const { data: clusters, pending, refresh } = await useAsyncData(
  'all-clusters',
  () => api.clustersList(),
  {}
)

const filteredClusters = computed(() => clusters.value?.filter(
  cluster => cluster.number.toString().includes(filterValueString.value.trim())
) ?? [])
</script>
