import { useUserStore } from '~/stores/user'

export default defineNuxtPlugin(() => {
  onNuxtReady(async () => {
    const userStore = useUserStore()
    userStore.refreshAuth()
  })
})
