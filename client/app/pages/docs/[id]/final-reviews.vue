<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="lg:col-span-full">
        <DocumentFinalReviews :heading-level="4" :name="draftName" />
      </div>

      <ErrorAlert v-if="approvalLogsListError" title="Error loading approval logs">
        Approval logs: {{ approvalLogsListError }}
      </ErrorAlert>
      <div
        class="w-full mt-6 grid grid-cols-1 grid-rows-1 place-items-stretch gap-x-8 gap-y-8 lg:grid-cols-3">
        <BaseCard class="lg:col-span-full grid place-items-stretch">
          <template #header>
            <CardHeader title="Approval Logs (public)" />
          </template>
          <div v-if="rfcToBe && rfcToBe.id" class="flex flex-col items-center space-y-4">
            <RpcApprovalLogTextarea v-if="rfcToBe" :draft-name="draftName" :reload="approvalLogsListReload"
              class="w-4/5 min-w-100" />
            <DocumentApprovalLogs :draft-name="draftName" :rfc-to-be-id="rfcToBe.id"
              :is-loading="approvalLogsListPending" :error="approvalLogsListError" :comment-list="approvalLogsList"
              :reload="approvalLogsListReload" class="w-3/5 min-w-100" />
          </div>
        </BaseCard>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { useAsyncData } from '#app'
import { type DocTabId } from '~/utils/doc'

const route = useRoute()
const api = useApi()

// COMPUTED

const currentTab: DocTabId = 'final-reviews'

const draftName = computed(() => route.params.id?.toString() ?? '')

const { data: rfcToBe, error: rfcToBeError, status: rfcToBeStatus, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  {
    server: false,
    lazy: true,
    deep: true // author editing relies on deep reactivity
  }
)

const {
  data: approvalLogsList,
  pending: approvalLogsListPending,
  error: approvalLogsListError,
  refresh: approvalLogsListReload
} = await useAsyncData(
  `approval-log-${draftName.value}`,
  () => api.documentsApprovalLogsList({ draftName: draftName.value }),
  { server: false, lazy: true }
)

</script>
