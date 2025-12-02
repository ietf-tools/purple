<template>
  <i v-if="status === 'pending'">
    Loading...
  </i>
  <div v-else-if="status === 'error'">
    {{ error }}
  </div>
  <div v-else-if="status === 'success' && cluster">
    <TitleBlock :title="`Cluster ${cluster.number}`" class="mb-5">
      <template #right>
        <div class="flex gap-3">
          <button @click="openAddModal" type="button"
            class="flex items-center rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
            <Icon name="uil:plus" class="-ml-1 h-5 w-5 mr-2" aria-hidden="true" />
            Add document
          </button>
        </div>
      </template>
    </TitleBlock>

    <DocumentDependenciesGraph :cluster="cluster" />

    <ClusterReorder :cluster="cluster" :on-success="refresh" class="max-w-96" />
  </div>
  <div v-else>
    Unknown cluster
  </div>
</template>

<script setup lang="ts">

import ClusterAddDocumentModal from '../../components/ClusterAddDocumentModal.vue'
import { overlayModalKey } from '~/providers/providerKeys'

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

const snackbar = useSnackbar()

const overlayModal = inject(overlayModalKey)

const openAddModal = () => {
  if (!cluster.value) {
    snackbar.add({
      type: 'warning',
      title: 'Still loading cluster...',
      text: 'Try again soon'
    })
    return
  }

  if (!overlayModal) {
    throw Error(`Expected modal provider ${JSON.stringify({ overlayModalKey })}`)
  }
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: ClusterAddDocumentModal,
    componentProps: {
      cluster: cluster.value,
      onSuccess: refresh
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
