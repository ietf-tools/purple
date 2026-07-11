<template>
  <div>
    <StatsTabs current-tab="stream" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="statsError" title="Error loading published-RFC stats">
        Published stats: {{ statsError }}
      </ErrorAlert>

      <BaseCard class="w-full grid place-items-stretch">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h3 class="text-base font-semibold leading-7">
            RFCs published by stream and status
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
          Count of RFCs published each period, grouped by publication stream and
          broken down by status. Streams and statuses with no publications in the
          shown range are omitted.
        </p>

        <div v-if="periods.length === 0" class="mt-4 px-3 py-3 text-center text-sm opacity-60">No data.</div>
        <template v-else>
          <div class="mt-3 flex items-center justify-end">
            <label class="flex items-center gap-2 text-sm">
              <input v-model="splitIetf" type="checkbox" class="rounded border-gray-300 dark:border-neutral-600">
              <span>Split IETF into WG / AD-sponsored</span>
            </label>
          </div>
          <GroupedStackedBars
            class="mt-2"
            :periods="periods"
            :streams="streams"
            :statuses="statuses"
            :stream-label="streamLabel"
          />

          <!-- Transposed: periods are columns, streams x status are rows. -->
          <div class="mt-6 w-full overflow-x-auto">
            <table class="w-full text-sm divide-y divide-gray-300 dark:divide-neutral-700 whitespace-nowrap">
              <thead class="bg-gray-50 dark:bg-neutral-800">
                <tr>
                  <th scope="col" class="py-2 pl-4 pr-3 text-left font-semibold">Stream / status</th>
                  <th v-for="p in periods" :key="p.label" scope="col" class="px-3 py-2 text-right font-semibold">
                    <div>{{ p.label }}</div>
                    <div v-if="showWeekRange" class="text-xs font-normal opacity-60">{{ weekRange(p) }}</div>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
                <template v-for="stream in streams" :key="stream">
                  <tr class="bg-gray-50 dark:bg-neutral-800">
                    <th :colspan="periods.length + 1" class="py-2 pl-4 pr-3 text-left font-semibold">
                      {{ streamLabel(stream) }}
                    </th>
                  </tr>
                  <tr v-for="status in statuses" :key="`${stream}-${status}`">
                    <th scope="row" class="py-1.5 pl-6 pr-3 text-left font-normal">
                      <span class="mr-2 inline-block h-2.5 w-2.5 rounded-sm align-middle" :style="{ backgroundColor: statusColor(status) }" />
                      {{ status }}
                    </th>
                    <td v-for="p in periods" :key="p.label" class="px-3 py-1.5 text-right tabular-nums">
                      {{ fmt(count(p, stream, status)) }}
                    </td>
                  </tr>
                  <tr class="border-t border-gray-200 dark:border-neutral-700">
                    <th scope="row" class="py-1.5 pl-6 pr-3 text-left font-medium opacity-80">{{ streamLabel(stream) }} total</th>
                    <td v-for="p in periods" :key="p.label" class="px-3 py-1.5 text-right tabular-nums font-medium">
                      {{ fmt(streamTotal(p, stream)) }}
                    </td>
                  </tr>
                </template>
                <tr class="border-t-4 border-gray-300 dark:border-neutral-600 bg-gray-50 dark:bg-neutral-800">
                  <th scope="row" class="py-2 pl-4 pr-3 text-left font-semibold">All streams</th>
                  <td v-for="p in periods" :key="p.label" class="px-3 py-2 text-right tabular-nums font-semibold">
                    {{ fmt(periodTotal(p)) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { StatsQueuePeriodEnum, type QueuePublishedStatPeriod, type QueuePublishedStats } from '~/purple_client'
import { statusColor } from '~/utils/statsViz'

const api = useApi()

const PERIOD_OPTIONS = [
  { value: StatsQueuePeriodEnum.Week, label: 'Weeks' },
  { value: StatsQueuePeriodEnum.Month, label: 'Months' },
  { value: StatsQueuePeriodEnum.Quarter, label: 'Quarters' },
  { value: StatsQueuePeriodEnum.Year, label: 'Years' },
  { value: StatsQueuePeriodEnum.Ietf, label: 'IETF meetings' }
]

const STREAM_LABELS: Record<string, string> = {
  ietf: 'IETF',
  'ietf-wg': 'IETF WG',
  'ietf-ad': 'IETF AD-sponsored',
  ise: 'ISE', irtf: 'IRTF', iab: 'IAB', editorial: 'Editorial'
}
const streamLabel = (slug: string): string => STREAM_LABELS[slug] ?? slug

// The backend always splits IETF into ietf-wg / ietf-ad; off (default) merges
// them back into a single "ietf" bucket. Client-side only — no refetch.
const splitIetf = ref(false)
const mergeStream = (slug: string) =>
  (!splitIetf.value && (slug === 'ietf-wg' || slug === 'ietf-ad')) ? 'ietf' : slug

// Deferred query controls: pending* bind to the inputs, applied* drive the query.
const pendingPeriod = ref<StatsQueuePeriodEnum>(StatsQueuePeriodEnum.Year)
const pendingCount = ref(4)
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
  pendingCount.value = c
  appliedPeriod.value = pendingPeriod.value
  appliedCount.value = c
}

const {
  data: stats,
  error: statsError,
  status: statsStatus
} = await useAsyncData(
  'stats-queue-published',
  () => api.statsQueuePublished({ period: appliedPeriod.value, count: appliedCount.value }),
  {
    server: false,
    lazy: true,
    watch: [appliedPeriod, appliedCount],
    default: () => ({ streams: [], statuses: [], periods: [] }) as QueuePublishedStats
  }
)

const rawPeriods = computed(() => stats.value?.periods ?? [])
const statuses = computed(() => stats.value?.statuses ?? [])

// Display streams, with ietf-wg/ietf-ad collapsed to ietf when not split.
const streams = computed(() => {
  const seen = new Set<string>()
  const out: string[] = []
  for (const s of stats.value?.streams ?? []) {
    const m = mergeStream(s)
    if (!seen.has(m)) { seen.add(m); out.push(m) }
  }
  return out
})

// Periods with counts re-aggregated under the merged stream keys.
const periods = computed<QueuePublishedStatPeriod[]>(() =>
  rawPeriods.value.map((p) => {
    const agg = new Map<string, { stream: string, status: string, count: number }>()
    for (const c of p.counts) {
      const stream = mergeStream(c.stream)
      const k = `${stream}|${c.status}`
      const cur = agg.get(k)
      if (cur) cur.count += c.count
      else agg.set(k, { stream, status: c.status, count: c.count })
    }
    return { ...p, counts: [...agg.values()] }
  })
)

// period label -> "stream|status" -> count
const lookup = computed(() => {
  const m = new Map<string, Map<string, number>>()
  for (const p of periods.value) {
    const cells = new Map<string, number>()
    for (const c of p.counts) cells.set(`${c.stream}|${c.status}`, c.count)
    m.set(p.label, cells)
  }
  return m
})
function count (p: QueuePublishedStatPeriod, stream: string, status: string): number {
  return lookup.value.get(p.label)?.get(`${stream}|${status}`) ?? 0
}
function streamTotal (p: QueuePublishedStatPeriod, stream: string): number {
  return statuses.value.reduce((sum, s) => sum + count(p, stream, s), 0)
}
function periodTotal (p: QueuePublishedStatPeriod): number {
  return p.counts.reduce((sum, c) => sum + c.count, 0)
}
const fmt = (n: number) => (n === 0 ? '—' : n.toLocaleString())

const showWeekRange = computed(() => /^\d{4}-W\d{2}$/.test(periods.value[0]?.label ?? ''))
function weekRange (p: QueuePublishedStatPeriod): string {
  const f = (d: Date) => d.toLocaleDateString('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' })
  const last = new Date(p.end.getTime() - 86400000)
  return `${f(p.start)} – ${f(last)}`
}

useHeadSafe({ title: 'RFCs published by stream' })
</script>
