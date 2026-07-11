<template>
  <div>
    <StatsTabs current-tab="time" />

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
          <!-- Period / range: deferred (the query can run long) — takes effect on Apply. -->
          <div class="flex flex-wrap items-center gap-2 text-sm">
            <label class="flex items-center gap-1">
              <span class="opacity-70">Period</span>
              <select v-model="pendingPeriod" class="rounded-md border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 py-1 pl-2 pr-8">
                <option v-for="p in PERIOD_OPTIONS" :key="p.value" :value="p.value">{{ p.label }}</option>
              </select>
            </label>
            <label class="flex items-center gap-1">
              <span class="opacity-70">Last</span>
              <input
                v-model.number="pendingCount"
                type="number" min="1" max="52"
                class="w-16 rounded-md border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-2 py-1"
                @keyup.enter="apply"
                @blur="pendingCount = clamp(pendingCount)"
              >
            </label>
            <button
              type="button"
              class="rounded-md px-3 py-1 font-medium text-white bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed"
              :disabled="!dirty || statsStatus === 'pending'"
              @click="apply"
            >Apply</button>
          </div>
        </div>

        <p class="mt-1 text-xs opacity-60">
          Each bin covers the documents in the queue during that period; bars show
          the time spent in each assignment role <em>within</em> the period (a
          per-period flow, not a running cumulative total).
        </p>

        <!-- View mode: immediate, drives both the chart and the summary table. -->
        <div class="mt-3 flex items-center justify-end gap-2 text-xs">
          <span class="opacity-60">View</span>
          <div class="inline-flex overflow-hidden rounded-md border border-gray-300 dark:border-neutral-600">
            <button
              type="button"
              class="px-2 py-1"
              :class="mode === 'calendar' ? 'bg-violet-600 text-white' : 'bg-white dark:bg-neutral-800'"
              @click="mode = 'calendar'"
            >Calendar days</button>
            <button
              type="button"
              class="px-2 py-1 border-l border-gray-300 dark:border-neutral-600"
              :class="mode === 'working' ? 'bg-violet-600 text-white' : 'bg-white dark:bg-neutral-800'"
              @click="mode = 'working'"
            >Working days</button>
            <button
              type="button"
              class="px-2 py-1 border-l border-gray-300 dark:border-neutral-600"
              :class="mode === 'share' ? 'bg-violet-600 text-white' : 'bg-white dark:bg-neutral-800'"
              @click="mode = 'share'"
            >Share %</button>
          </div>
        </div>

        <div class="mt-2">
          <StackedTimeBars
            :periods="periods"
            :mode="mode === 'share' ? 'share' : 'total'"
            :day-scale="mode === 'working' ? workingScale : 1"
          />
        </div>
      </BaseCard>

      <!-- Per-role summary table -->
      <BaseCard class="mt-8 w-full grid place-items-stretch">
        <h3 class="text-base font-semibold leading-7 mb-2">Summary by period</h3>
        <div v-if="periods.length === 0" class="px-3 py-3 text-center text-sm opacity-60">No data.</div>
        <!-- Transposed: periods are columns, metrics are rows. -->
        <div v-else class="w-full overflow-x-auto">
          <table class="w-full text-sm divide-y divide-gray-300 dark:divide-neutral-700 whitespace-nowrap">
            <thead class="bg-gray-50 dark:bg-neutral-800">
              <tr>
                <th scope="col" class="py-2 pl-4 pr-3 text-left font-semibold">Period</th>
                <th v-for="p in periods" :key="p.label" scope="col" class="px-3 py-2 text-right font-semibold">
                  <div>{{ p.label }}</div>
                  <div v-if="showWeekRange" class="text-xs font-normal opacity-60">{{ weekRange(p) }}</div>
                  <div v-if="p.legacyIncluded" class="text-xs font-normal text-violet-500" title="Includes pre-transition labeled states">legacy</div>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
              <tr class="bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Docs</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">{{ p.docCount }}</td>
              </tr>

              <!-- Not blocked section: the total heads the section, roles below. -->
              <tr class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Not blocked</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ cellValue(p, p.totalWorkingSeconds) }}
                </td>
              </tr>
              <tr v-for="role in notBlockedRoles" :key="role">
                <th scope="row" class="py-2 pl-8 pr-3 text-left font-normal">{{ role }}</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums">
                  {{ cellValue(p, secondsFor(p, role)) }}
                </td>
              </tr>

              <!-- Blocked section. -->
              <tr class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold text-red-600 dark:text-red-400">Blocked</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ cellValue(p, p.totalBlockedSeconds) }}
                </td>
              </tr>
              <tr v-for="role in blockedRoles" :key="role">
                <th scope="row" class="py-2 pl-8 pr-3 text-left font-normal text-red-600 dark:text-red-400">{{ role }}</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums">
                  {{ cellValue(p, secondsFor(p, role)) }}
                </td>
              </tr>

              <!-- Grand total + blocked share (day views only; both are
                   redundant in the share view). -->
              <tr v-if="mode !== 'share'" class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">Total time</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ cellValue(p, p.totalWorkingSeconds + p.totalBlockedSeconds) }}
                </td>
              </tr>
              <tr v-if="mode !== 'share'" class="bg-gray-50 dark:bg-neutral-800">
                <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">% Blocked</th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                  {{ blockedPct(p) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="mode === 'working'" class="mt-2 px-1 text-xs opacity-60">
          Working days are calculated assuming an average of {{ workingHoursPerYear }} working hours per year.
        </p>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { StatsQueuePeriodEnum, type QueuePeriodStat, type QueueStats } from '~/purple_client'
import { formatDays, orderedRoles } from '~/utils/timeline'

const api = useApi()

const PERIOD_OPTIONS = [
  { value: StatsQueuePeriodEnum.Week, label: 'Weeks' },
  { value: StatsQueuePeriodEnum.Month, label: 'Months' },
  { value: StatsQueuePeriodEnum.Quarter, label: 'Quarters' },
  { value: StatsQueuePeriodEnum.Year, label: 'Years' },
  { value: StatsQueuePeriodEnum.Ietf, label: 'IETF meetings' }
]

// View mode (client-side, immediate): calendar days, working days (calendar
// scaled by working-hours/year over total hours/year), or per-period share (%).
const mode = ref<'calendar' | 'working' | 'share'>('calendar')

const HOURS_PER_YEAR = 365 * 24 // 8760
const workingHoursPerYear = Number(useRuntimeConfig().public.workingHoursPerYear) || 2000
const workingScale = computed(() => workingHoursPerYear / HOURS_PER_YEAR)

// Query controls are deferred: `pending*` bind to the inputs, `applied*` drive
// the (potentially long) query and only change when Apply is pressed.
const pendingPeriod = ref<StatsQueuePeriodEnum>(StatsQueuePeriodEnum.Month)
const pendingCount = ref(6)
const appliedPeriod = ref<StatsQueuePeriodEnum>(pendingPeriod.value)
const appliedCount = ref(clamp(pendingCount.value))

function clamp (n: number): number {
  return Math.min(Math.max(Math.trunc(n || 1), 1), 52)
}

const dirty = computed(() =>
  pendingPeriod.value !== appliedPeriod.value || clamp(pendingCount.value) !== appliedCount.value
)

function apply () {
  const c = clamp(pendingCount.value)
  pendingCount.value = c // reflect any clamping back into the input
  appliedPeriod.value = pendingPeriod.value
  appliedCount.value = c
}

const {
  data: stats,
  error: statsError,
  status: statsStatus
} = await useAsyncData(
  'stats-queue',
  () => api.statsQueue({ period: appliedPeriod.value, count: appliedCount.value }),
  {
    server: false,
    lazy: true,
    watch: [appliedPeriod, appliedCount],
    default: () => ({ periods: [] }) as QueueStats
  }
)

const periods = computed(() => stats.value?.periods ?? [])

// Week labels (2026-W28) are terse; show the covered date range beneath them.
// Keyed off the displayed data, not appliedPeriod, so stale rows during a
// refetch keep their correct sublabels.
const showWeekRange = computed(() => /^\d{4}-W\d{2}$/.test(periods.value[0]?.label ?? ''))
function weekRange (p: QueuePeriodStat): string {
  const fmt = (d: Date) =>
    d.toLocaleDateString('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' })
  const last = new Date(p.end.getTime() - 86400000) // end is exclusive (next Monday)
  return `${fmt(p.start)} – ${fmt(last)}`
}

// Ordered union of roles across all periods (not-blocked first, then blocked).
const roleColumns = computed(() => {
  const seen = new Map<string, boolean>()
  for (const p of periods.value) {
    for (const r of p.byRole) seen.set(r.role, r.isBlocked)
  }
  return orderedRoles([...seen].map(([role, isBlocked]) => ({ role, isBlocked })))
})

const blockedRoleSet = computed(() => {
  const s = new Set<string>()
  for (const p of periods.value) {
    for (const r of p.byRole) if (r.isBlocked) s.add(r.role)
  }
  return s
})

// Roles split into the two table sections, preserving the ordered union.
const notBlockedRoles = computed(() => roleColumns.value.filter(r => !blockedRoleSet.value.has(r)))
const blockedRoles = computed(() => roleColumns.value.filter(r => blockedRoleSet.value.has(r)))

function secondsFor (p: QueuePeriodStat, role: string): number {
  return p.byRole.find(r => r.role === role)?.seconds ?? 0
}

// A value's share of the period total, as a percent ("—"/"<1%" like cells).
function sharePct (p: QueuePeriodStat, seconds: number): string {
  const total = p.totalWorkingSeconds + p.totalBlockedSeconds
  if (total <= 0 || seconds <= 0) return '—'
  const pct = Math.round((seconds / total) * 100)
  return pct === 0 ? '<1%' : `${pct}%`
}

// A table cell: whole (calendar or working) days, or the value's share of the
// period total (%). "—" = no time; "<1%" = some time that rounds below 1%.
function cellValue (p: QueuePeriodStat, seconds: number): string {
  if (mode.value === 'share') return sharePct(p, seconds)
  const scale = mode.value === 'working' ? workingScale.value : 1
  return formatDays(seconds * scale)
}

// Blocked share of the period's total time (shown in the whole-day view).
function blockedPct (p: QueuePeriodStat): string {
  return sharePct(p, p.totalBlockedSeconds)
}

useHeadSafe({ title: 'Queue statistics' })
</script>
