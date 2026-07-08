<template>
  <div class="w-full">
    <div ref="container" class="relative w-full overflow-x-auto text-gray-600 dark:text-neutral-300">
      <svg ref="svgEl" :width="width" :height="height" class="block" />
      <div
        v-if="tooltip.visible"
        class="pointer-events-none absolute z-10 rounded-md border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-2 py-1 text-xs shadow-lg text-gray-800 dark:text-neutral-100"
        :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }"
      >
        <div class="font-semibold">{{ tooltip.title }}</div>
        <div>{{ tooltip.detail }}</div>
      </div>
      <div v-if="periods.length === 0" class="py-8 text-center text-sm opacity-60">
        No data for the selected range.
      </div>
    </div>
    <!-- Role legend, grouped blocked vs not-blocked. -->
    <div v-if="orderedRoles.length" class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs">
      <span v-for="role in orderedRoles" :key="role" class="flex items-center gap-1">
        <span class="inline-block h-3 w-3 rounded-sm" :style="{ backgroundColor: colorOf(role) }" />
        {{ role }}<span v-if="blockedRoles.has(role)" class="opacity-50"> (blocked)</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'
import type { QueuePeriodStat } from '~/purple_client'
import { humanSeconds, roleColorScale } from '~/utils/timeline'

type Props = {
  periods: QueuePeriodStat[]
}
const props = defineProps<Props>()

const container = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const width = ref(720)
const height = 340

const MARGIN = { top: 16, right: 16, bottom: 52, left: 64 }

const tooltip = reactive({ visible: false, x: 0, y: 0, title: '', detail: '' })

const periods = computed(() => props.periods)

// Union of roles across all periods, plus color/order and a blocked lookup.
const roleScale = computed(() => {
  const seen = new Map<string, boolean>()
  for (const p of periods.value) {
    for (const r of p.byRole) {
      seen.set(r.role, r.isBlocked)
    }
  }
  const roles = [...seen].map(([role, isBlocked]) => ({ role, isBlocked }))
  return roleColorScale(roles)
})
const orderedRoles = computed(() => roleScale.value.ordered)
const colorOf = (role: string) => roleScale.value.colorOf(role)
const blockedRoles = computed(() => {
  const s = new Set<string>()
  for (const p of periods.value) {
    for (const r of p.byRole) {
      if (r.isBlocked) s.add(r.role)
    }
  }
  return s
})

function secondsFor (p: QueuePeriodStat, role: string): number {
  return p.byRole.find(r => r.role === role)?.seconds ?? 0
}

function draw () {
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
  if (!svgEl.value || periods.value.length === 0) return

  const data = periods.value
  const roles = orderedRoles.value
  const innerW = Math.max(width.value - MARGIN.left - MARGIN.right, 10)
  const innerH = height - MARGIN.top - MARGIN.bottom

  const x = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([MARGIN.left, MARGIN.left + innerW])
    .padding(0.25)

  const maxY = d3.max(data, d => d.totalBlockedSeconds + d.totalWorkingSeconds) ?? 0
  const y = d3.scaleLinear()
    .domain([0, maxY === 0 ? 1 : maxY])
    .range([MARGIN.top + innerH, MARGIN.top])
    .nice()

  const yAxis = d3.axisLeft(y).ticks(5).tickFormat(d => `${Math.round(Number(d) / 86400)}d`)
  const yG = svg.append('g').attr('transform', `translate(${MARGIN.left}, 0)`).call(yAxis)
  yG.selectAll('text').attr('fill', 'currentColor').attr('font-size', 10)
  yG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  const xAxis = d3.axisBottom(x)
  const xG = svg.append('g').attr('transform', `translate(0, ${MARGIN.top + innerH})`).call(xAxis)
  xG.selectAll('text')
    .attr('fill', 'currentColor').attr('font-size', 10)
    .attr('transform', 'rotate(-25)').attr('text-anchor', 'end')
  xG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  const bandW = x.bandwidth()

  data.forEach(d => {
    const bx = x(d.label) ?? 0
    let cursor = 0 // running total (seconds) from the bottom
    for (const role of roles) {
      const secs = secondsFor(d, role)
      if (secs <= 0) continue
      const yTop = y(cursor + secs)
      const yBottom = y(cursor)
      svg.append('rect')
        .attr('x', bx).attr('y', yTop)
        .attr('width', bandW).attr('height', Math.max(yBottom - yTop, 0))
        .attr('fill', colorOf(role))
        .style('cursor', 'pointer')
        .on('mousemove', (e: MouseEvent) => showTooltip(e, d, role, secs))
        .on('mouseleave', hideTooltip)
      cursor += secs
    }

    if (d.legacyIncluded) {
      svg.append('text')
        .attr('x', bx + bandW / 2).attr('y', MARGIN.top + innerH + 2)
        .attr('text-anchor', 'middle').attr('fill', '#a78bfa').attr('font-size', 8)
        .text('legacy')
    }
  })
}

function showTooltip (event: MouseEvent, d: QueuePeriodStat, role: string, seconds: number) {
  const rect = container.value?.getBoundingClientRect()
  tooltip.visible = true
  tooltip.x = event.clientX - (rect?.left ?? 0) + 12
  tooltip.y = event.clientY - (rect?.top ?? 0) + 12
  const tag = blockedRoles.value.has(role) ? 'blocked' : 'not blocked'
  tooltip.title = `${d.label} — ${role} (${tag})`
  tooltip.detail = `${humanSeconds(seconds)} · ${d.docCount} docs`
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
      if (w && Math.abs(w - width.value) > 1) width.value = w
    })
    observer.observe(container.value)
  }
  draw()
})
onBeforeUnmount(() => observer?.disconnect())

watch([periods, width], () => draw())
</script>
