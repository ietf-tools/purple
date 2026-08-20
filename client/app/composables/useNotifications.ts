import { ref, onBeforeMount, onUnmounted, readonly } from 'vue'
import type { PurpleApi } from '~/purple_client'
import { useUserStore } from '~/stores/user'

// Shared singleton: one poll drives the header bell no matter how many
// components read the count (mirrors the useCurrentTime pattern).
const POLL_MS = 60_000
const unreadCount = ref(0)
let interval: ReturnType<typeof setInterval> | null = null
let instanceCount = 0
let api: PurpleApi | null = null

const poll = async () => {
  if (!api) return
  try {
    const { count } = await api.notificationsUnreadCount()
    unreadCount.value = count
  } catch {
    // transient network/auth errors: keep the last known count
  }
}

export const useNotifications = () => {
  api = useApi()
  const userStore = useUserStore()

  onBeforeMount(() => {
    instanceCount++
    if (userStore.authenticated) void poll()
    if (interval === null) {
      interval = setInterval(poll, POLL_MS)
    }
  })
  onUnmounted(() => {
    instanceCount--
    if (instanceCount <= 0 && interval !== null) {
      clearInterval(interval)
      interval = null
    }
  })

  const markAllRead = async () => {
    if (!api) return
    await api.notificationsMarkRead()
    unreadCount.value = 0
  }

  return {
    unreadCount: readonly(unreadCount),
    refresh: poll,
    markAllRead
  }
}
