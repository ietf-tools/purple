<template>
  <FinalReviewsInProgress :name="props.name" :heading-level="4" />
  <ErrorAlert v-if="error" title="API Error for Done / PUB">
    {{ error }}
  </ErrorAlert>
  <FinalReviewsDone :queue-items="queueItemsFilterDone" :error="error" :status="status" :heading-level="4" />
  <FinalReviewsForPublication :queue-items="queueItemsFilterPublisher" :error="error" :status="status"
    :heading-level="4" />
</template>

<script setup lang="ts">
import type { QueueItem } from '~/purple_client';

type Props = {
  name?: string
  headingLevel?: HeadingLevel
}

const props = withDefaults(defineProps<Props>(), { headingLevel: 2 })

const api = useApi()

const {
  data: queueList,
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

const queueListWithFilters = computed(() => {
  if (!props.name) {
    return queueList.value
  }
  return queueList.value.filter(queueItem => {
    queueItem.name == props.name
  })
})

const ASSIGNMENT_SET_ROLE_PUBLISHER = 'publisher'

const queueItemsFilterPublisher = computed((): QueueItem[] => {
  return queueListWithFilters.value?.filter(
    queueItem => queueItem.assignmentSet?.some(
      assignmentSetItem => assignmentSetItem.role === ASSIGNMENT_SET_ROLE_PUBLISHER
    )
  ) ?? []
})

const queueItemsFilterDone = computed((): QueueItem[] => {
  return queueListWithFilters.value?.filter(
    queueItem => queueItemsFilterPublisher.value.every(queueItemPublisher => queueItemPublisher.id !== queueItem.id)
  ) ?? []
})
</script>
