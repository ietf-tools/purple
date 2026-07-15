<template>
  <div class="w-full">
    <div ref="container" class="relative w-full overflow-x-auto text-gray-600 dark:text-neutral-300">
      <svg
        ref="svgEl" :width="chartWidth" :height="HEIGHT_PX" class="block"
        role="img" aria-label="Grouped bar chart of RFCs published each period, one bar per stream stacked by status. The same data is in the table below."
      />
      <div
        v-if="tooltip.visible"
        class="pointer-events-none absolute z-10 max-w-xs rounded-md border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-2 py-1 text-xs shadow-lg text-gray-800 dark:text-neutral-100"
        :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
      >
        <div class="font-semibold">{{ tooltip.title }}</div>
        <div>{{ tooltip.detail }}</div>
      </div>
      <div v-if="periods.length === 0" class="py-8 text-center text-sm opacity-60">
        No data for the selected range.
      </div>
    </div>

    <!-- Interactive legend: click a status to hide/show it (chart rescales). -->
    <div v-if="statuses.length" class="mt-3 text-xs">
      <p class="mb-1 opacity-50">Color = status; each group is one period, one bar per stream. Click a status to hide it.</p>
      <div class="flex flex-wrap gap-x-4 gap-y-1">
        <button
          v-for="s in statuses" :key="s"
          type="button"
          :aria-pressed="!hidden.has(s)"
          class="flex items-center gap-1 rounded px-1 transition-opacity hover:bg-gray-100 dark:hover:bg-neutral-800"
          :class="hidden.has(s) ? 'opacity-35' : ''"
          @click="toggle(s)"
        >
          <span
            class="inline-block h-3 w-3 rounded-sm ring-1 ring-inset ring-black/10"
            :style="{ backgroundColor: statusColor(s) }"
          />
          <span :class="hidden.has(s) ? 'line-through' : ''">{{ s }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import * as d3 from 'd3'
import { statusColor, type Status, type Stream, type StreamPeriod } from '~/utils/statsViz'

type Props = {
  periods: StreamPeriod[]
  streams: Stream[] // active streams, display order
  statuses: Status[] // active status buckets, display order
  streamLabel: (slug: Stream) => string
}
const props = defineProps<Props>()

const container = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const { width: containerWidth } = useElementSize(container) // reactive (VueUse)
const chartWidth = ref(720)
const HEIGHT_PX = 340
const MARGIN = { top: 16, right: 16, bottom: 56, left: 44 }
const SEG_GAP_PX = 1
const MIN_BAR_W_PX = 16 // min px per stream sub-bar, else the chart scrolls

const hidden = reactive(new Set<string>())
function toggle (key: string) {
  if (hidden.has(key)) hidden.delete(key)
  else hidden.add(key)
}

const tooltip = reactive({ visible: false, x: 0, y: 0, title: '', detail: '' })

const periods = computed(() => props.periods)
const visibleStatuses = computed(() => props.statuses.filter(s => !hidden.has(s)))

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
function countOf (label: string, stream: Stream, status: Status): number {
  return lookup.value.get(label)?.get(`${stream}|${status}`) ?? 0
}
function stackTotal (label: string, stream: Stream): number {
  return visibleStatuses.value.reduce((sum, s) => sum + countOf(label, stream, s), 0)
}

function draw () {
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
  hideTooltip()
  if (!svgEl.value || periods.value.length === 0) return

  const data = periods.value
  const streams = props.streams
  // Scroll horizontally when the groups need more than the container's width.
  const groupW = streams.length * MIN_BAR_W_PX + 24
  const needed = MARGIN.left + MARGIN.right + data.length * groupW
  chartWidth.value = Math.max(containerWidth.value, needed)
  const innerW = chartWidth.value - MARGIN.left - MARGIN.right
  const innerH = HEIGHT_PX - MARGIN.top - MARGIN.bottom

  const x0 = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([MARGIN.left, MARGIN.left + innerW])
    .paddingInner(0.25).paddingOuter(0.1)
  const x1 = d3.scaleBand<string>()
    .domain(streams)
    .range([0, x0.bandwidth()])
    .padding(0.15)

  const maxCount = d3.max(
    data.flatMap(d => streams.map(s => stackTotal(d.label, s)))
  ) ?? 0
  const y = d3.scaleLinear()
    .domain([0, maxCount === 0 ? 1 : maxCount])
    .range([MARGIN.top + innerH, MARGIN.top])
    .nice()

  const yAxis = d3.axisLeft(y).ticks(5).tickFormat(d => `${d}`)
  const yG = svg.append('g').attr('transform', `translate(${MARGIN.left}, 0)`).call(yAxis)
  yG.selectAll('text').attr('fill', 'currentColor').attr('font-size', 10)
  yG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  const baseline = MARGIN.top + innerH
  svg.append('line')
    .attr('x1', MARGIN.left).attr('x2', MARGIN.left + innerW)
    .attr('y1', baseline).attr('y2', baseline)
    .attr('stroke', 'currentColor').attr('opacity', 0.3)

  const barW = x1.bandwidth()
  data.forEach((d) => {
    const gx = x0(d.label) ?? 0
    for (const stream of streams) {
      const sx = gx + (x1(stream) ?? 0)
      let cursor = 0
      for (const status of visibleStatuses.value) {
        const c = countOf(d.label, stream, status)
        if (c <= 0) continue
        const yTop = y(cursor + c)
        const h = Math.max(y(cursor) - yTop - SEG_GAP_PX, 0)
        if (h > 0) {
          svg.append('rect')
            .attr('x', sx).attr('y', yTop)
            .attr('width', barW).attr('height', h)
            .attr('rx', 1)
            .attr('fill', statusColor(status))
            .style('cursor', 'pointer')
            .on('mousemove', (e: MouseEvent) => showTooltip(e, d.label, stream, status, c))
            .on('mouseleave', hideTooltip)
        }
        cursor += c
      }
      // Stream label under each sub-bar (rotated to fit narrow bars).
      svg.append('text')
        .attr('x', sx + barW / 2).attr('y', baseline + 4)
        .attr('transform', `rotate(-45, ${sx + barW / 2}, ${baseline + 4})`)
        .attr('text-anchor', 'end').attr('fill', 'currentColor')
        .attr('font-size', 8).attr('opacity', 0.7)
        .text(props.streamLabel(stream))
    }
    // Period label centered under the group.
    svg.append('text')
      .attr('x', gx + x0.bandwidth() / 2).attr('y', HEIGHT_PX - 6)
      .attr('text-anchor', 'middle').attr('fill', 'currentColor')
      .attr('font-size', 10).attr('font-weight', 600)
      .text(d.label)
  })
}

function showTooltip (event: MouseEvent, label: string, stream: Stream, status: Status, count: number) {
  const el = container.value
  const rect = el?.getBoundingClientRect()
  // Offset by the container's scroll so the tooltip tracks the pointer when the
  // grouped chart is scrolled horizontally.
  tooltip.x = event.clientX - (rect?.left ?? 0) + (el?.scrollLeft ?? 0) + 12
  tooltip.y = event.clientY - (rect?.top ?? 0) + (el?.scrollTop ?? 0) + 12
  tooltip.visible = true
  tooltip.title = `${label} — ${props.streamLabel(stream)}`
  tooltip.detail = `${status}: ${count} RFC${count === 1 ? '' : 's'}`
}
function hideTooltip () {
  tooltip.visible = false
}

// useElementSize drives the first paint and resizes; the watch redraws on data,
// width, legend toggles, or stream-set changes — no manual ResizeObserver.
watch([periods, containerWidth, visibleStatuses, () => props.streams], () => draw())
</script>
