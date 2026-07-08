<template>
  <div ref="container" class="relative w-full overflow-x-auto text-gray-600 dark:text-neutral-300">
    <svg ref="svgEl" :width="width" :height="height" class="block" />
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
import * as d3 from 'd3'
import { DateTime } from 'luxon'
import type { AssignmentTimeline, TimelineSegment } from '~/purple_client'
import { KIND_LABELS, humanMillis, kindColor, segmentEnd, segmentMillis } from '~/utils/timeline'

type Props = {
  timeline: AssignmentTimeline
}
const props = defineProps<Props>()

type Lane = {
  key: string
  label: string
  sublabel?: string
  segments: TimelineSegment[]
  group: 'summary' | 'legacy' | 'track'
}

const container = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const width = ref(720)

const ROW_H = 26
const ROW_GAP = 6
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

// Build the lanes: summary bands first, then legacy states, then per-assignment.
const lanes = computed<Lane[]>(() => {
  const tl = props.timeline
  const result: Lane[] = []
  for (const band of tl.summary) {
    if (band.segments.length === 0) continue
    result.push({
      key: `summary-${band.kind}`,
      label: KIND_LABELS[band.kind] ?? band.kind,
      segments: band.segments,
      group: 'summary'
    })
  }
  for (const band of tl.legacy) {
    result.push({
      key: `legacy-${band.label}`,
      label: band.label ?? '(label)',
      sublabel: 'legacy',
      segments: band.segments,
      group: 'legacy'
    })
  }
  for (const track of tl.tracks) {
    result.push({
      key: `track-${track.assignmentId}`,
      label: track.role,
      sublabel: track.personName ?? undefined,
      segments: track.segments,
      group: 'track'
    })
  }
  return result
})

const height = computed(() =>
  MARGIN.top + MARGIN.bottom + lanes.value.length * (ROW_H + ROW_GAP)
)

function draw () {
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
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

  // Top time axis.
  const axis = d3.axisTop(x).ticks(Math.max(2, Math.floor(innerWidth / 110)))
  const axisG = svg.append('g')
    .attr('transform', `translate(0, ${MARGIN.top})`)
    .call(axis)
  axisG.selectAll('text').attr('fill', 'currentColor').attr('font-size', 10)
  axisG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  const rowY = (i: number) => MARGIN.top + i * (ROW_H + ROW_GAP)

  // Transition marker.
  const tx = x(props.timeline.transitionDate)
  if (tx >= MARGIN.left && tx <= MARGIN.left + innerWidth) {
    svg.append('line')
      .attr('x1', tx).attr('x2', tx)
      .attr('y1', MARGIN.top).attr('y2', height.value - MARGIN.bottom)
      .attr('stroke', '#8b5cf6').attr('stroke-dasharray', '4 3').attr('opacity', 0.8)
    svg.append('text')
      .attr('x', tx + 3).attr('y', MARGIN.top - 16)
      .attr('fill', '#8b5cf6').attr('font-size', 9)
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

    // Segments.
    svg.selectAll(`.seg-${i}`)
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
  const rect = container.value?.getBoundingClientRect()
  const fmt = (dt: Date) => DateTime.fromJSDate(dt).toLocaleString(DateTime.DATE_MED)
  tooltip.visible = true
  tooltip.x = event.clientX - (rect?.left ?? 0) + 12
  tooltip.y = event.clientY - (rect?.top ?? 0) + 12
  tooltip.title = lane.sublabel ? `${lane.label} — ${lane.sublabel}` : lane.label
  tooltip.detail = `${fmt(seg.start)} → ${seg.end ? fmt(seg.end) : 'ongoing'}`
  tooltip.duration = humanMillis(segmentMillis(seg, now))
}

function hideTooltip () {
  tooltip.visible = false
}

let observer: ResizeObserver | null = null
onMounted(() => {
  if (container.value) {
    width.value = container.value.clientWidth
    observer = new ResizeObserver(entries => {
      const w = entries[0]?.contentRect.width
      if (w && Math.abs(w - width.value) > 1) {
        width.value = w
      }
    })
    observer.observe(container.value)
  }
  draw()
})
onBeforeUnmount(() => observer?.disconnect())

watch([lanes, width], () => draw())
</script>
