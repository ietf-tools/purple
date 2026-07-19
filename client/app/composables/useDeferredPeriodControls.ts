import { clamp } from 'lodash-es'
import type { StatsQueuePeriodEnum } from '~/purple_client'

const MIN_COUNT = 1
const MAX_COUNT = 52

/** Count coerced to an integer in [1, 52]; empty / NaN / 0 become 1. */
export function clampCount(n: number): number {
  return clamp(Math.trunc(n || 1), MIN_COUNT, MAX_COUNT)
}

/**
 * Deferred period/count controls shared by the stats tabs (Time, Counts,
 * Stream). `pending*` bind to the inputs; `applied*` drive the (potentially
 * long) query and only change when `apply()` is called — pass the `applied*`
 * refs to useAsyncData's `watch`. `isDirty` reflects whether an Apply is due.
 */
export function useDeferredPeriodControls(
  initialPeriod: StatsQueuePeriodEnum,
  initialCount: number
) {
  const pendingPeriod = ref<StatsQueuePeriodEnum>(initialPeriod)
  const pendingCount = ref(initialCount)
  const appliedPeriod = ref<StatsQueuePeriodEnum>(initialPeriod)
  const appliedCount = ref(clampCount(initialCount))

  const isDirty = computed(
    () =>
      pendingPeriod.value !== appliedPeriod.value ||
      clampCount(pendingCount.value) !== appliedCount.value
  )

  function apply() {
    const count = clampCount(pendingCount.value)
    pendingCount.value = count // reflect any clamping back into the input
    appliedPeriod.value = pendingPeriod.value
    appliedCount.value = count
  }

  return {
    pendingPeriod,
    pendingCount,
    appliedPeriod,
    appliedCount,
    isDirty,
    apply,
    clampCount
  }
}
