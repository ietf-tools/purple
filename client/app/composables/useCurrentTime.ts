import { ref, onBeforeMount, onUnmounted, readonly } from 'vue'
import { DateTime } from 'luxon'

const getNowUtc = () => DateTime.now().setZone('utc')
const currentTime = ref(getNowUtc())
let interval: null | ReturnType<typeof setInterval> = null
let instanceCount = 0

export const useCurrentTime = () => {
  onBeforeMount(() => {
    instanceCount++
    if (interval === null) {
      interval = setInterval(() => { currentTime.value = getNowUtc() }, 1000)
    }
  })
  onUnmounted(() => {
    instanceCount--
    // only clear interval after last component using us is unmounted
    if ((instanceCount <= 0) && (interval !== null)) {
      clearInterval(interval)
      interval = null
    }
  })
  return readonly(currentTime)
}
