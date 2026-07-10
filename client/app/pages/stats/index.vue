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
        <div v-if="periods.length === 0" class="px-3 py-3 text-center text-sm opacity-60">No data.</div>
        <!-- Transposed: periods are columns, metrics are rows. -->
        <div v-else class="w-full overflow-x-auto">
          <table class="w-full text-sm divide-y divide-gray-300 dark:divide-neutral-700 whitespace-nowrap">
            <thead class="bg-gray-50 dark:bg-neutral-800">
              <tr>
                <th class="py-2 pl-4 pr-3 text-left font-semibold">Period</th>
                <th v-for="p in periods" :key="p.label" class="px-3 py-2 text-right font-semibold">
                  <div>{{ p.label }}</div>
                  <div v-if="p.legacyIncluded" class="text-xs font-normal text-violet-500" title="Includes pre-transition labeled states">legacy</div>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
              <tr class="border-b-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Docs</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">{{ p.docCount }}</td>
              </tr>
              <tr v-for="role in roleColumns" :key="role">
                <th
                  scope="row"
                  class="py-2 pl-4 pr-3 text-left font-medium"
                  :class="blockedRoleSet.has(role) ? 'text-red-600 dark:text-red-400' : ''"
                >{{ role }}</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums">
                  {{ formatDays(secondsFor(p, role)) }}
                </td>
              </tr>
              <tr class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Not blocked</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ formatDays(p.totalWorkingSeconds) }}
                </td>
              </tr>
              <tr class="bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Blocked</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ formatDays(p.totalBlockedSeconds) }}
                </td>
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
