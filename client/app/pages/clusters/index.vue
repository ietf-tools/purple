<template>
  <div>
    <TitleBlock title="Cluster Management">
      <template #right>
        <RefreshButton :pending="pending" class="mr-3" @refresh="refresh" />
        <ClusterNew :on-success="refresh" :last-cluster-number="lastClusterNumber" />
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
          <Anchor :href="`/clusters/${cluster.number}/`" :class="ANCHOR_STYLE">
            Cluster {{ cluster.number }}
          </Anchor>
        </h2>
        <ul class="flex flex-wrap pt-1 gap-y-1 gap-x-3 text-xs leading-[1]">
          <li class="whitespace-nowrap inline-block" v-for="(document, index) in cluster.documents" :key="index">
            <DocumentCardMini :document="document" />
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RefreshButton from '~/components/RefreshButton.vue'

useHead({
  title: 'Manage Clusters'
})

const filterValueString = ref('')

const api = useApi()

const { data: clusters, pending, refresh } = await useAsyncData(
  'all-clusters',
  () => api.clustersList(),
  {}
)

const lastClusterNumber = computed(() => {
  if (!clusters.value) return 0
  return Math.max(...clusters.value.map(cluster => cluster.number))
})

const clusterSearch = computed(() => clusters.value ? clusters.value.map(cluster => JSON.stringify(cluster)) : [])

const filteredClusters = computed(() => clusters.value?.filter(
  (_cluster, index) => clusterSearch.value[index] ? clusterSearch.value[index].includes(filterValueString.value.trim()) : false
).sort((a, b) => b.number - a.number) ?? [])
</script>
