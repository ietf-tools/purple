<template>
  <div class="container mx-auto p-6 max-w-3xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Notifications</h1>
      <RefreshButton :pending="pending" @refresh="refresh" />
    </div>

    <div v-if="pending && items.length === 0" class="py-8 text-center text-gray-500">
      Loading notifications...
    </div>

    <ErrorAlert v-else-if="error" title="Error loading notifications">
      {{ error }}
    </ErrorAlert>

    <div v-else-if="items.length === 0" class="py-12 text-center text-gray-500">
      Nothing here yet.
    </div>

    <ul v-else class="divide-y divide-gray-100 dark:divide-gray-700">
      <li v-for="n in items" :key="n.id">
        <Anchor
          :href="`/docs/${n.draftName}/assignments`"
          class="flex items-start gap-3 py-3 px-2 -mx-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
          :class="n.unread ? 'bg-violet-50/60 dark:bg-violet-900/20' : ''">
          <span
            class="mt-2 h-2 w-2 shrink-0 rounded-full"
            :class="n.unread ? 'bg-violet-600' : 'bg-transparent'"
            aria-hidden="true" />
          <Icon
            :name="
              n.eventType === 'blocked'
                ? 'solar:lock-keyhole-bold-duotone'
                : 'solar:lock-keyhole-unlocked-bold-duotone'
            "
            :class="n.eventType === 'blocked' ? 'text-red-500' : 'text-green-600'"
            class="mt-0.5 h-5 w-5 shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-sm text-gray-900 dark:text-gray-100">
              <span class="font-semibold">{{ n.draftName }}</span>
              was {{ n.eventType === 'blocked' ? 'blocked' : 'unblocked' }}
            </div>
            <div
              v-if="n.eventType === 'blocked' && n.reasons?.length"
              class="mt-1 flex flex-wrap gap-1">
              <BaseBadge v-for="reason in n.reasons" :key="reason" :label="reason" />
            </div>
          </div>
          <time
            class="shrink-0 text-xs text-gray-400 dark:text-gray-500"
            :title="n.created?.toISOString()">
            {{ relativeTime(n.created) }}
          </time>
        </Anchor>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'

const api = useApi()
const { markAllRead } = useNotifications()

const { data, pending, error, refresh } = await useAsyncData(
  'notifications',
  () => api.notificationsList(),
  {
    server: false,
    lazy: true
  }
)

const items = computed(() => data.value?.results ?? [])

const relativeTime = (d?: Date) => (d ? (DateTime.fromJSDate(d).toRelative() ?? '') : '')

// Visiting the page clears the bell dot; the unread highlights above stay for
// this render (they came from the list fetched before the watermark advanced).
onMounted(markAllRead)

useHeadSafe({ title: 'Notifications' })
</script>
