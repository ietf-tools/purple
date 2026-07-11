<template>
  <div>
    <DocHeader :draft-name="draftName" :rfc-to-be="rfcToBe" @withdrawn="rfcToBeRefresh" />

    <DocTabs :current-tab="currentTab" :draft-name="draftName" />

    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ErrorAlert v-if="timelineError" title="Error loading timeline">
        Timeline: {{ timelineError }}
      </ErrorAlert>

      <BaseCard class="w-full grid place-items-stretch">
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold leading-7">
            Assignment timeline
            <Icon v-show="timelineStatus === 'pending'" name="ei:spinner-3" size="1.5em" class="animate-spin" />
          </h3>
          <div class="flex items-center gap-3 text-xs">
            <span class="flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-sm" :style="{ backgroundColor: KIND_COLORS[KIND_WORKING] }" />
              Not blocked
            </span>
            <span class="flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-sm" :style="{ backgroundColor: KIND_COLORS[KIND_BLOCKED] }" />
              Blocked
            </span>
            <span class="flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-sm" :style="{ backgroundColor: KIND_COLORS[KIND_AWAITING] }" />
              Awaiting ref
            </span>
            <span class="flex items-center gap-1">
              <span class="inline-block h-3 w-3 rounded-sm" :style="{ backgroundColor: KIND_COLORS[KIND_LEGACY] }" />
              Legacy state
            </span>
          </div>
        </div>

        <div v-if="timeline" class="mt-4">
          <TimelineGantt :timeline="timeline" />
        </div>
      </BaseCard>

      <!-- Summary + per-assignment table -->
      <BaseCard v-if="timeline" class="mt-8 w-full grid place-items-stretch">
        <h3 class="text-base font-semibold leading-7 mb-2">Time in assignments</h3>
        <table class="w-full divide-y divide-gray-300 dark:divide-neutral-700 text-sm">
          <thead class="bg-gray-50 dark:bg-neutral-800">
            <tr>
              <th scope="col" class="py-2 pl-4 pr-3 text-left font-semibold">Assignment</th>
              <th scope="col" class="px-3 py-2 text-left font-semibold">Assignee</th>
              <th scope="col" class="px-3 py-2 text-right font-semibold">Not blocked</th>
              <th scope="col" class="px-3 py-2 text-right font-semibold">Blocked</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
            <tr v-for="row in trackRows" :key="row.key">
              <td class="py-2 pl-4 pr-3">
                <BaseBadge :label="row.role" />
                <span v-if="row.awaiting" class="ml-2 text-xs opacity-60">awaiting ref</span>
              </td>
              <td class="px-3 py-2">{{ row.person ?? '—' }}</td>
              <td class="px-3 py-2 text-right">{{ row.isBlocked ? '—' : humanMillis(row.millis) }}</td>
              <td class="px-3 py-2 text-right">{{ row.isBlocked ? humanMillis(row.millis) : '—' }}</td>
            </tr>
            <tr v-if="trackRows.length === 0">
              <td colspan="4" class="px-3 py-3 text-center opacity-60">No assignments yet.</td>
            </tr>
          </tbody>
          <tfoot class="border-t-2 border-gray-300 dark:border-neutral-600 font-semibold">
            <tr>
              <td class="py-2 pl-4 pr-3" colspan="2">Total</td>
              <td class="px-3 py-2 text-right">{{ humanMillis(totalWorkingMillis) }}</td>
              <td class="px-3 py-2 text-right">{{ humanMillis(totalBlockedMillis) }}</td>
            </tr>
          </tfoot>
        </table>
      </BaseCard>

      <!-- Legacy labeled states (pre-transition) -->
      <BaseCard v-if="legacyRows.length > 0" class="mt-8 w-full grid place-items-stretch">
        <h3 class="text-base font-semibold leading-7 mb-2">
          Legacy labeled states
          <span class="text-xs font-normal opacity-60">(before {{ transitionDateLabel }})</span>
        </h3>
        <table class="w-full divide-y divide-gray-300 dark:divide-neutral-700 text-sm">
          <thead class="bg-gray-50 dark:bg-neutral-800">
            <tr>
              <th scope="col" class="py-2 pl-4 pr-3 text-left font-semibold">State</th>
              <th scope="col" class="px-3 py-2 text-left font-semibold">Counts as</th>
              <th scope="col" class="px-3 py-2 text-right font-semibold">Time</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-neutral-800">
            <tr v-for="row in legacyRows" :key="row.key">
              <td class="py-2 pl-4 pr-3">{{ row.label }}</td>
              <td class="px-3 py-2">{{ row.kind === KIND_BLOCKED ? 'Blocked' : 'Not blocked' }}</td>
              <td class="px-3 py-2 text-right">{{ humanMillis(row.millis) }}</td>
            </tr>
          </tbody>
        </table>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DateTime } from 'luxon'
import { type DocTabId } from '~/utils/doc'
import {
  KIND_AWAITING,
  KIND_BLOCKED,
  KIND_COLORS,
  KIND_LEGACY,
  KIND_WORKING,
  humanMillis,
  totalMillis
} from '~/utils/timeline'

const route = useRoute()
const api = useApi()

const currentTab: DocTabId = 'timeline'
const draftName = computed(() => route.params.id?.toString() ?? '')

const {
  data: timeline,
  error: timelineError,
  status: timelineStatus
} = await useAsyncData(
  () => `timeline-${draftName.value}`,
  () => api.documentAssignmentTimeline({ draftName: draftName.value }),
  { server: false, lazy: true }
)

const { data: rfcToBe, refresh: rfcToBeRefresh } = await useAsyncData(
  () => `timeline-draft-${draftName.value}`,
  () => api.documentsRetrieve({ draftName: draftName.value }),
  { server: false, lazy: true, deep: true }
)

const now = new Date()

const trackRows = computed(() =>
  (timeline.value?.tracks ?? []).map((track) => {
    // A final-review assignment can yield two tracks with the same assignmentId
    // — a working row and an "awaiting ref" (blocked) row; segments carry the
    // kind. Disambiguate the key and mark the awaiting row (as the gantt does).
    const awaiting = track.segments.some(s => s.kind === KIND_AWAITING)
    return {
      key: `track-${track.assignmentId}-${awaiting ? 'awaiting' : 'main'}`,
      role: track.role,
      awaiting,
      person: track.personName,
      isBlocked: track.isBlocked,
      millis: totalMillis(track.segments, now)
    }
  })
)

const totalWorkingMillis = computed(() => {
  const band = (timeline.value?.summary ?? []).find(b => b.kind === KIND_WORKING)
  return band ? totalMillis(band.segments, now) : 0
})

const totalBlockedMillis = computed(() => {
  const band = (timeline.value?.summary ?? []).find(b => b.kind === KIND_BLOCKED)
  return band ? totalMillis(band.segments, now) : 0
})

const legacyRows = computed(() =>
  (timeline.value?.legacy ?? []).map(band => ({
    key: `legacy-${band.label}`,
    label: band.label ?? '(label)',
    kind: band.kind,
    millis: totalMillis(band.segments, now)
  }))
)

const transitionDateLabel = computed(() =>
  timeline.value
    ? DateTime.fromJSDate(timeline.value.transitionDate).toLocaleString(DateTime.DATE_MED)
    : ''
)

useHeadSafe({ title: `${draftName.value} timeline` })
</script>
