<template>
  <i v-if="status === 'pending'">
    Loading...
  </i>
  <div v-else-if="status === 'error'">
    {{ error }}
  </div>
  <div v-else-if="status === 'success' && cluster">
    Cluster {{ cluster.number }}

    {{ JSON.stringify(cluster) }}
    <ol>
      <li v-for="(document, index) in cluster.documents" :key="`${index}${document.name}`">
        {{ document.name }}
      </li>
    </ol>

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
  title: `Manage Cluster ${clusterNumber}`
})

const api = useApi()

// DATA

const state = reactive({
  createDialogShown: false,
  notifDialogShown: false,
  notifDialogMessage: ''
})

// METHODS

const { data: cluster, error, status, refresh } = await useAsyncData(
  () => `cluster-${clusterNumber.value}`,
  () => {
    if(clusterNumber.value === undefined) {
      return Promise.resolve(null)
    }
    return api.clustersRetrieve({ number: clusterNumber.value })
  }
)

</script>
