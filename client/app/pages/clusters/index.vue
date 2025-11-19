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

    <div class="flex flex-col gap-5 mt-5">
      <div v-for="cluster in clusters" :key="cluster.number" class="flex flex-row items-start">
        <h2 class="flex flex-row items-start text-lg whitespace-nowrap grow-0 shrink-0 w-[7em]">
          <a :href="`/clusters/${cluster.number}/`" :class="ANCHOR_STYLE">
            Cluster {{ cluster.number }}
          </a>
        </h2>
        <ul class="flex flex-wrap gap-2 text-xs">
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

const api = useApi()

const { data: clusters, pending, refresh } = await useAsyncData(
  'all-clusters',
  () => api.clustersList(),
  {}
)

</script>
