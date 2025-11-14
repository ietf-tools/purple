<template>
  <div>
    <TitleBlock
      title="Final Review (formerly AUTH48)"
      summary="Where the magic mercifully stops happening."/>

    <FinalReviewInProgress />

    <ErrorAlert v-if="error" title="API Error for Done / PUB">
      {{ error }}
    </ErrorAlert>
    <FinalReviewDone
      :queue-items="queueItemsFilterDone"
      :error="error"
      :status="status"
    />
    <FinalReviewForPublication
      :queue-items="queueItemsFilterPublisher"
      :error="error"
      :status="status"
    />
  </div>
</template>

<script setup lang="ts">
import type { QueueItem } from '~/purple_client';

const api = useApi()

const {
  data,
  pending,
  status,
  refresh,
  error,
} = await useAsyncData(
  'final-review-pending-false',
  () => api.queueList({ pendingFinalApproval: false }),
  {
    server: false,
    lazy: true,
    default: () => [] as QueueItem[],
  }
)

const ASSIGNMENT_SET_ROLE_PUBLISHER = 'publisher'

const queueItemsFilterPublisher = computed((): QueueItem[] => {
  return data.value?.filter(
    queueItem => queueItem.assignmentSet?.some(
      assignmentSetItem => assignmentSetItem.role === ASSIGNMENT_SET_ROLE_PUBLISHER
    )
  ) ?? []
})

const queueItemsFilterDone = computed((): QueueItem[] => {
  return data.value?.filter(
    queueItem => queueItemsFilterPublisher.value.every(queueItemPublisher => queueItemPublisher.id !== queueItem.id)
  ) ?? []
})

</script>
