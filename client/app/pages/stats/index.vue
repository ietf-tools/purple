<template>
  <div>
    <StatsTabs current-tab="queue" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="statsError" title="Error loading queue stats">
        Queue stats: {{ statsError }}
      </ErrorAlert>

      <BaseCard class="w-full grid place-items-stretch">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h3 class="text-base font-semibold leading-7">
            Time in assignments across the queue
            <Icon v-show="statsStatus === 'pending'" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          </h3>
          <div class="flex flex-wrap items-center gap-2 text-sm">
            <label class="flex items-center gap-1">
              <span class="opacity-70">Period</span>
              <select v-model="period" class="rounded-md border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-2 py-1">
                <option v-for="p in PERIOD_OPTIONS" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </label>
            <label class="flex items-center gap-1">
              <span class="opacity-70">Last</span>
              <input
                v-model.number="count"
                type="number" min="1" max="52"
                class="w-16 rounded-md border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-2 py-1"
              >
            </label>
          </div>
        </div>

        <p class="mt-1 text-xs opacity-60">
          Each bin covers the documents in the queue during that period; bars show
          the time spent in each assignment role <em>within</em> the period (a
          per-period flow, not a running cumulative total).
        </p>

        <div class="mt-3">
          <StackedTimeBars :periods="periods" />
        </div>
      </BaseCard>

      <!-- Per-role summary table (whole-day granularity) -->
      <BaseCard class="mt-8 w-full grid place-items-stretch">
        <h3 class="text-base font-semibold leading-7 mb-2">Summary by period</h3>
        <div class="w-full overflow-x-auto">
          <table class="w-full text-sm divide-y divide-gray-300 dark:divide-neutral-700 whitespace-nowrap">
            <thead class="bg-gray-50 dark:bg-neutral-800">
              <tr>
                <th class="py-2 pl-4 pr-3 text-left font-semibold">Period</th>
                <th class="px-3 py-2 text-right font-semibold">Docs</th>
                <th
                  v-for="role in roleColumns" :key="role"
                  class="px-3 py-2 text-right font-semibold"
                  :class="blockedRoleSet.has(role) ? 'text-red-600 dark:text-red-400' : ''"
                >{{ role }}</th>
                <th class="px-3 py-2 text-right font-semibold border-l border-gray-300 dark:border-neutral-700">Not blocked</th>
                <th class="px-3 py-2 text-right font-semibold">Blocked</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
              <tr v-for="p in periods" :key="p.label">
                <td class="py-2 pl-4 pr-3">
                  {{ p.label }}
                  <span v-if="p.legacyIncluded" class="ml-1 text-xs text-violet-500" title="Includes pre-transition labeled states">legacy</span>
                </td>
                <td class="px-3 py-2 text-right">{{ p.docCount }}</td>
                <td v-for="role in roleColumns" :key="role" class="px-3 py-2 text-right tabular-nums">
                  {{ formatDays(secondsFor(p, role)) }}
                </td>
                <td class="px-3 py-2 text-right tabular-nums font-medium border-l border-gray-300 dark:border-neutral-700">
                  {{ formatDays(p.totalWorkingSeconds) }}
                </td>
                <td class="px-3 py-2 text-right tabular-nums font-medium">
                  {{ formatDays(p.totalBlockedSeconds) }}
                </td>
              </tr>
              <tr v-if="periods.length === 0">
                <td :colspan="roleColumns.length + 4" class="px-3 py-3 text-center opacity-60">No data.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { StatsQueuePeriodEnum, type QueuePeriodStat, type QueueStats } from '~/purple_client'
import { formatDays, roleColorScale } from '~/utils/timeline'

const api = useApi()

const PERIOD_OPTIONS = [
  { value: StatsQueuePeriodEnum.Week, label: 'Weeks' },
  { value: StatsQueuePeriodEnum.Month, label: 'Months' },
  { value: StatsQueuePeriodEnum.Quarter, label: 'Quarters' },
  { value: StatsQueuePeriodEnum.Year, label: 'Years' }
]

const period = ref<StatsQueuePeriodEnum>(StatsQueuePeriodEnum.Month)
const count = ref(6)
const clampedCount = computed(() => Math.min(Math.max(Math.trunc(count.value || 1), 1), 52))

const {
  data: stats,
  error: statsError,
  status: statsStatus
} = await useAsyncData(
  'stats-queue',
  () => api.statsQueue({ period: period.value, count: clampedCount.value }),
  {
    server: false,
    lazy: true,
    watch: [period, clampedCount],
    default: () => ({ periods: [] }) as QueueStats
  }
)

const periods = computed(() => stats.value?.periods ?? [])

// Ordered union of roles across all periods (not-blocked first, then blocked).
const roleColumns = computed(() => {
  const seen = new Map<string, boolean>()
  for (const p of periods.value) {
    for (const r of p.byRole) seen.set(r.role, r.isBlocked)
  }
  return roleColorScale([...seen].map(([role, isBlocked]) => ({ role, isBlocked }))).ordered
})

const blockedRoleSet = computed(() => {
  const s = new Set<string>()
  for (const p of periods.value) {
    for (const r of p.byRole) if (r.isBlocked) s.add(r.role)
  }
  return s
})

function secondsFor (p: QueuePeriodStat, role: string): number {
  return p.byRole.find(r => r.role === role)?.seconds ?? 0
}

useHeadSafe({ title: 'Queue statistics' })
</script>
