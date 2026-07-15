<template>
  <div ref="container" class="relative w-full overflow-x-auto text-gray-600 dark:text-neutral-300">
    <svg
      ref="svgEl" :width="width" :height="height" class="block"
      role="img" aria-label="Timeline showing when this document was in each assignment state, blocked, or a legacy state."
    />
    <div
      v-if="tooltip.visible"
      class="pointer-events-none absolute z-10 rounded-md border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-2 py-1 text-xs shadow-lg text-gray-800 dark:text-neutral-100"
      :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
    >
      <div class="font-semibold">{{ tooltip.title }}</div>
      <div>{{ tooltip.detail }}</div>
      <div class="opacity-70">{{ tooltip.duration }}</div>
    </div>
    <div v-if="lanes.length === 0" class="py-8 text-center text-sm opacity-60">
      No assignment or state history to display.
    </div>
  </div>
</template>

<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import * as d3 from 'd3'
import { DateTime } from 'luxon'
import type { AssignmentTimeline, TimelineSegment } from '~/purple_client'
import { KIND_AWAITING, KIND_LEGACY_COLOR, humanMillis, kindColor, kindLabel, segmentEnd, segmentMillis } from '~/utils/statsViz'

type Props = {
  timeline: AssignmentTimeline
}
const props = defineProps<Props>()

type Lane = {
  key: string
  label: string
  sublabel?: string
  segments: TimelineSegment[]
  group: 'summary' | 'blocked-reason' | 'legacy' | 'track'
}

const container = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const { width } = useElementSize(container) // reactive container width (VueUse)

const ROW_H = 26
const ROW_GAP = 6
const GROUP_GAP = 20 // extra space setting the summary lanes apart from the detail lanes
const MARGIN = { top: 28, right: 16, bottom: 8, left: 180 }

const now = new Date()

const tooltip = reactive({
  visible: false,
  x: 0,
  y: 0,
  title: '',
  detail: '',
  duration: ''
})

// Earliest segment start of a lane (Infinity if it has none), for ordering.
function firstStart (segments: TimelineSegment[]): number {
  let min = Infinity
  for (const seg of segments) min = Math.min(min, seg.start.getTime())
  return min
}

// Summary lanes stay pinned at the top (the boxed section); every detail lane
// below — blocking reasons, legacy states, per-assignment tracks — is ordered
// by its first appearance in time.
const lanes = computed<Lane[]>(() => {
  const tl = props.timeline
  const summary: Lane[] = []
  for (const band of tl.summary) {
    if (band.segments.length === 0) continue
    summary.push({
      key: `summary-${band.kind}`,
      label: kindLabel(band.kind),
      segments: band.segments,
      group: 'summary'
    })
  }

  const detail: Lane[] = []
  for (const band of tl.blockedReasons) {
    if (band.segments.length === 0) continue
    detail.push({
      key: `blocked-reason-${band.label}`,
      label: band.label ?? '(reason)',
      sublabel: 'blocked reason',
      segments: band.segments,
      group: 'blocked-reason'
    })
  }
  for (const band of tl.legacy) {
    if (band.segments.length === 0) continue
    detail.push({
      key: `legacy-${band.label}`,
      label: band.label ?? '(label)',
      sublabel: 'legacy',
      segments: band.segments,
      group: 'legacy'
    })
  }
  for (const track of tl.tracks) {
    // A final_review_editor assignment is split by the backend into a working
    // row and an "awaiting ref" row (segments carry the kind); label each.
    const awaiting = track.segments.some(s => s.kind === KIND_AWAITING)
    detail.push({
      key: `track-${track.assignmentId}-${awaiting ? 'awaiting' : 'main'}`,
      label: track.role,
      sublabel: awaiting ? 'awaiting ref' : (track.personName ?? undefined),
      segments: track.segments,
      group: 'track'
    })
  }
  detail.sort((a, b) => firstStart(a.segments) - firstStart(b.segments))

  return [...summary, ...detail]
})

// The leading summary lanes ("Not blocked" / "Blocked") aggregate the detail
// lanes below them, so they get boxed together and set apart with a gap.
const summaryCount = computed(() => lanes.value.filter(l => l.group === 'summary').length)
const hasGroupSplit = computed(() =>
  summaryCount.value > 0 && summaryCount.value < lanes.value.length
)

const height = computed(() =>
  MARGIN.top + MARGIN.bottom + lanes.value.length * (ROW_H + ROW_GAP)
  + (hasGroupSplit.value ? GROUP_GAP : 0)
)

function draw () {
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
  hideTooltip() // removing a hovered element never fires mouseleave
  if (!svgEl.value || lanes.value.length === 0) return

  const laneList = lanes.value
  const innerWidth = Math.max(width.value - MARGIN.left - MARGIN.right, 10)

  // Time domain across every segment plus the transition boundary.
  const starts: Date[] = []
  const ends: Date[] = []
  for (const lane of laneList) {
    for (const seg of lane.segments) {
      starts.push(seg.start)
      ends.push(segmentEnd(seg, now))
    }
  }
  starts.push(props.timeline.transitionDate)
  ends.push(props.timeline.transitionDate)
  const minDate = d3.min(starts) ?? props.timeline.transitionDate
  const maxDate = d3.max(ends) ?? now
  const x = d3.scaleTime()
    .domain([minDate, maxDate === minDate ? now : maxDate])
    .range([MARGIN.left, MARGIN.left + innerWidth])
    .nice()

  const summaryN = summaryCount.value
  const rowY = (i: number) =>
    MARGIN.top + i * (ROW_H + ROW_GAP) + (i >= summaryN ? GROUP_GAP : 0)

  // Box the summary lanes so it reads that they summarise the detail lanes,
  // which are set apart below by GROUP_GAP. Drawn first, behind everything.
  if (summaryN > 0) {
    const boxTop = rowY(0) - 3
    const boxBottom = rowY(summaryN - 1) + ROW_H + 3
    svg.append('rect')
      .attr('x', 4).attr('y', boxTop)
      .attr('width', Math.max(width.value - 8, 10))
      .attr('height', boxBottom - boxTop)
      .attr('fill', 'currentColor').attr('opacity', 0.06).attr('rx', 6)
    if (hasGroupSplit.value) {
      const yDiv = (rowY(summaryN - 1) + ROW_H + rowY(summaryN)) / 2
      svg.append('line')
        .attr('x1', 4).attr('x2', Math.max(width.value - 4, 10))
        .attr('y1', yDiv).attr('y2', yDiv)
        .attr('stroke', 'currentColor').attr('opacity', 0.15)
    }
  }

  // Top time axis.
  const axis = d3.axisTop(x).ticks(Math.max(2, Math.floor(innerWidth / 110)))
  const axisG = svg.append('g')
    .attr('transform', `translate(0, ${MARGIN.top})`)
    .call(axis)
  axisG.selectAll('text').attr('fill', 'currentColor').attr('font-size', 10)
  axisG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  // Transition marker.
  const tx = x(props.timeline.transitionDate)
  if (tx >= MARGIN.left && tx <= MARGIN.left + innerWidth) {
    svg.append('line')
      .attr('x1', tx).attr('x2', tx)
      .attr('y1', MARGIN.top).attr('y2', height.value - MARGIN.bottom)
      .attr('stroke', KIND_LEGACY_COLOR).attr('stroke-dasharray', '4 3').attr('opacity', 0.8)
    svg.append('text')
      .attr('x', tx + 3).attr('y', MARGIN.top - 16)
      .attr('fill', KIND_LEGACY_COLOR).attr('font-size', 9)
      .text('transition')
  }

  // Lanes.
  laneList.forEach((lane, i) => {
    const y = rowY(i)

    // Row label.
    svg.append('text')
      .attr('x', MARGIN.left - 8).attr('y', y + ROW_H / 2)
      .attr('text-anchor', 'end').attr('dominant-baseline', 'middle')
      .attr('fill', 'currentColor')
      .attr('font-size', 11)
      .attr('font-weight', lane.group === 'summary' ? 600 : 400)
      .text(lane.label)
    if (lane.sublabel) {
      svg.append('text')
        .attr('x', MARGIN.left - 8).attr('y', y + ROW_H / 2 + 11)
        .attr('text-anchor', 'end').attr('fill', 'currentColor')
        .attr('font-size', 9).attr('opacity', 0.6)
        .text(lane.sublabel)
    }

    // Lane background.
    svg.append('rect')
      .attr('x', MARGIN.left).attr('y', y)
      .attr('width', innerWidth).attr('height', ROW_H)
      .attr('fill', 'currentColor').attr('opacity', 0.04).attr('rx', 3)

    // Segments. selectAll(null) forces an all-enter join (the SVG is rebuilt
    // each draw), avoiding a phantom class selector that matched nothing.
    svg.selectAll(null)
      .data(lane.segments)
      .enter()
      .append('rect')
      .attr('x', d => x(d.start))
      .attr('y', y + 2)
      .attr('width', d => Math.max(x(segmentEnd(d, now)) - x(d.start), 2))
      .attr('height', ROW_H - 4)
      .attr('rx', 2)
      .attr('fill', d => kindColor(d.kind))
      .attr('opacity', 0.85)
      .style('cursor', 'pointer')
      .on('mousemove', (event: MouseEvent, d: TimelineSegment) => showTooltip(event, lane, d))
      .on('mouseleave', hideTooltip)
  })
}

function showTooltip (event: MouseEvent, lane: Lane, seg: TimelineSegment) {
  const el = container.value
  const rect = el?.getBoundingClientRect()
  const fmt = (dt: Date) => DateTime.fromJSDate(dt).toLocaleString(DateTime.DATE_MED)
  // Offset by the container's scroll so the tooltip tracks the pointer when the
  // timeline is scrolled horizontally.
  tooltip.x = event.clientX - (rect?.left ?? 0) + (el?.scrollLeft ?? 0) + 12
  tooltip.y = event.clientY - (rect?.top ?? 0) + (el?.scrollTop ?? 0) + 12
  tooltip.visible = true
  tooltip.title = lane.sublabel ? `${lane.label} — ${lane.sublabel}` : lane.label
  tooltip.detail = `${fmt(seg.start)} → ${seg.end ? fmt(seg.end) : 'ongoing'}`
  tooltip.duration = humanMillis(segmentMillis(seg, now))
}

function hideTooltip () {
  tooltip.visible = false
}

// useElementSize reports the container width after mount and on resize, which
// drives the first paint; the watch redraws on that or on lane changes.
watch([lanes, width], () => draw())
</script>
