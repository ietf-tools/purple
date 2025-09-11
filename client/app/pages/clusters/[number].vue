<template>
  <div v-if="cluster">
    Cluster {{ cluster.number }}
    <ol>
      <li v-for="document in cluster.documents" :key="document.id">
        {{ document.name }}
      </li>
    </ol>
  </div>
  <div v-else>
    Unknown cluster
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

// Only allow numbers as route parameter, rejecting leading zeros
definePageMeta({ validate: route => /^[1-9]\d*$/.test(route.params.number.toString()) })

const clusterNumber = route.params.number

useHead({
  title: `Manage Cluster ${clusterNumber}`
})

// DATA

const state = reactive({
  createDialogShown: false,
  notifDialogShown: false,
  notifDialogMessage: ''
})

// METHODS

type Cluster = {
  number: number
  documents: { name: string }[]
}

const { data: cluster, pending, refresh } = await useFetch<Cluster>(`/api/rpc/clusters/${clusterNumber}`, {
  baseURL: '/',
  server: false,
  onRequestError ({ error }) {
    state.notifDialogMessage = error.toString()
    state.notifDialogShown = true
  },
  onResponseError ({ response, error }) {
    state.notifDialogMessage = response.statusText ?? error
    state.notifDialogShown = true
  }
})
</script>
