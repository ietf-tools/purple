<template>
  <div>
    <StatsTabs current-tab="counts" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="statsError" title="Error loading queue counts">
        Queue counts: {{ statsError }}
      </ErrorAlert>

      <BaseCard class="w-full grid place-items-stretch">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h3 class="text-base font-semibold leading-7">
            Document counts across the queue
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
                @blur="pendingCount = clampCount(pendingCount)"
              >
            </label>
            <button
              type="button"
              class="rounded-md px-3 py-1 font-medium text-white bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed"
              :disabled="!isDirty || statsStatus === 'pending'"
              @click="apply"
            >Apply</button>
          </div>
        </div>

        <p class="mt-1 text-xs opacity-60">
          Counts of documents and pages moving through the queue each period.
          Page counts are summed over the documents involved.
        </p>

        <div v-if="periods.length === 0" class="mt-4 px-3 py-3 text-center text-sm opacity-60">No data.</div>
        <!-- Transposed: periods are columns, metrics are rows. -->
        <div v-else class="mt-4 w-full overflow-x-auto">
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
                <th :colspan="periods.length + 1" class="py-2 pl-4 pr-3 text-left font-semibold">Doc counts</th>
              </tr>
              <tr v-for="(row, i) in docCountRows" :key="`doc-${i}`">
                <th scope="row" class="py-2 pl-6 pr-3 text-left font-normal" :class="row.divider ? dividerClass : ''">
                  {{ row.label }}
                  <span v-if="row.note" class="block whitespace-normal text-xs opacity-60">{{ row.note }}</span>
                </th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums" :class="row.divider ? dividerClass : ''">
                  {{ row.format(row.get(p)) }}
                </td>
              </tr>
              <tr class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                <th :colspan="periods.length + 1" class="py-2 pl-4 pr-3 text-left font-semibold">Page counts</th>
              </tr>
              <tr v-for="(row, i) in pageCountRows" :key="`page-${i}`">
                <th scope="row" class="py-2 pl-6 pr-3 text-left font-normal" :class="row.divider ? dividerClass : ''">
                  {{ row.label }}
                  <span v-if="row.note" class="block whitespace-normal text-xs opacity-60">{{ row.note }}</span>
                </th>
                <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums" :class="row.divider ? dividerClass : ''">
                  {{ row.format(row.get(p)) }}
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
import { StatsQueuePeriodEnum, type QueueCountStatPeriod, type QueueCountStats } from '~/purple_client'

const api = useApi()

const PERIOD_OPTIONS = [
  { value: StatsQueuePeriodEnum.Week, label: 'Weeks' },
  { value: StatsQueuePeriodEnum.Month, label: 'Months' },
  { value: StatsQueuePeriodEnum.Quarter, label: 'Quarters' },
  { value: StatsQueuePeriodEnum.Year, label: 'Years' },
  { value: StatsQueuePeriodEnum.Ietf, label: 'IETF meetings' }
]

// Deferred period/count controls (shared across the stats tabs).
const {
  pendingPeriod, pendingCount, appliedPeriod, appliedCount, isDirty, apply, clampCount
} = useDeferredPeriodControls(StatsQueuePeriodEnum.Month, 6)

const {
  data: stats,
  error: statsError,
  status: statsStatus
} = await useAsyncData(
  'stats-queue-counts',
  () => api.statsQueueCounts({ period: appliedPeriod.value, count: appliedCount.value }),
  {
    server: false,
    lazy: true,
    watch: [appliedPeriod, appliedCount],
    default: () => ({ periods: [] }) as QueueCountStats
  }
)

const periods = computed(() => stats.value?.periods ?? [])

// Week labels (2026-W28) are terse; show the covered date range beneath them.
// Keyed off the displayed data, not appliedPeriod, so stale rows during a
// refetch keep their correct sublabels.
const showWeekRange = computed(() => /^\d{4}-W\d{2}$/.test(periods.value[0]?.label ?? ''))
function weekRange (p: QueueCountStatPeriod): string {
  const fmt = (d: Date) =>
    d.toLocaleDateString('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' })
  const last = new Date(p.end.getTime() - 86400000) // end is exclusive (next Monday)
  return `${fmt(p.start)} – ${fmt(last)}`
}

// Heavier line under a row, to offset the group above from what follows.
const dividerClass = 'border-b-2 border-gray-500 dark:border-neutral-400'

const int = (n: number) => n.toLocaleString()
const pct = (n: number) => `${n}%`

type MetricRow = {
  label: string
  note?: string // long qualifier, folded onto its own line
  divider?: boolean // heavier bottom border, to offset the rows above
  get: (p: QueueCountStatPeriod) => number
  format: (n: number) => string
}

const docCountRows: MetricRow[] = [
  { label: 'Docs in queue at start', get: p => p.docsAtStart, format: int },
  { label: 'Docs entered', get: p => p.docsEntered, format: int },
  { label: 'RFCs published', divider: true, get: p => p.rfcsPublished, format: int },
  { label: 'Docs blocked entire period', get: p => p.docsBlockedEntire, format: int },
  { label: 'Docs entering with missing references', get: p => p.docsEnteredMissingRef, format: int },
  { label: 'Avg % time blocked', note: '(all docs)', get: p => p.avgPctBlockedAll, format: pct },
  { label: 'Avg % time blocked', note: '(docs not blocked at any point in period)', get: p => p.avgPctBlocked, format: pct }
]

const pageCountRows: MetricRow[] = [
  { label: 'Pages at start', get: p => p.pagesAtStart, format: int },
  { label: 'Pages entered', get: p => p.pagesEntered, format: int },
  { label: 'Pages published', divider: true, get: p => p.pagesPublished, format: int },
  { label: 'Pages gone to edit', get: p => p.pagesToEdit, format: int },
  { label: 'Pages blocked at end of period', get: p => p.pagesBlockedEnd, format: int },
  { label: 'Pages in progress at end of period', get: p => p.pagesInProgressEnd, format: int }
]

useHeadSafe({ title: 'Queue counts' })
</script>
