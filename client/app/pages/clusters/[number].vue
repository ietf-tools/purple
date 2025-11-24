<template>
  <i v-if="status === 'pending'">
    Loading...
  </i>
  <div v-else-if="status === 'error'">
    {{ error }}
  </div>
  <div v-else-if="status === 'success' && cluster">
    <h1>Cluster {{ cluster.number }}</h1>
    <DocumentDependenciesGraph :cluster="cluster" />
  </div>
  <div v-else>
    Unknown cluster
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

// Only allow numbers as route parameter, rejecting leading zeros
definePageMeta({ validate: route => /^[1-9]\d*$/.test(route.params.number?.toString() ?? '') })

const clusterNumber = computed(() => route.params.number ? parseInt(route.params.number.toString(), 10) : undefined)

useHead({
  title: `Manage Cluster ${clusterNumber.value}`
})

const api = useApi()

const { data: cluster, error, status, refresh } = await useAsyncData(
  () => `cluster-${clusterNumber.value}`,
  async () => {
    if (clusterNumber.value === undefined) {
      return null
    }
    return api.clustersRetrieve({ number: clusterNumber.value })
  }
)
</script>
