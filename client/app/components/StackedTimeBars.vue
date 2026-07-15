<template>
  <div class="w-full">
    <div ref="root" class="relative">
      <div ref="container" class="w-full overflow-x-auto text-gray-600 dark:text-neutral-300">
        <svg
          ref="svgEl" :width="width" :height="HEIGHT_PX" class="block"
          role="img" aria-label="Stacked bar chart of time spent per assignment role each period. The same data is in the table below."
        />
        <div v-if="periods.length === 0" class="py-8 text-center text-sm opacity-60">
          No data for the selected range.
        </div>
      </div>
      <!-- Tooltip lives outside the scrolling container so it can't be clipped
           or add to the scroll width; tooltipPosition flips it near edges. -->
      <div
        v-if="tooltip.visible"
        class="pointer-events-none absolute z-10 max-w-xs rounded-md border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-2 py-1 text-xs shadow-lg text-gray-800 dark:text-neutral-100"
        :style="tooltip.pos"
      >
        <div class="font-semibold">{{ tooltip.title }}</div>
        <div>{{ tooltip.detail }}</div>
        <div v-if="tooltip.members" class="mt-0.5 opacity-70">{{ tooltip.members }}</div>
      </div>
    </div>

    <!-- Interactive legend: click a category to hide/show it (chart rescales). -->
    <div v-if="categories.length" class="mt-3 text-xs">
      <p class="mb-1 opacity-50">Click to hide a category; the chart rescales. Minor roles are grouped as “Other”.</p>
      <div class="flex flex-wrap gap-x-4 gap-y-1">
        <button
          v-for="cat in categories" :key="cat.key"
          type="button"
          :aria-pressed="!hidden.has(cat.key)"
          class="flex items-center gap-1 rounded px-1 transition-opacity hover:bg-gray-100 dark:hover:bg-neutral-800"
          :class="hidden.has(cat.key) ? 'opacity-35' : ''"
          :title="cat.isOther ? cat.members.join(', ') : ''"
          @click="toggle(cat.key)"
        >
          <span
            class="inline-block h-3 w-3 rounded-sm ring-1 ring-inset ring-black/10"
            :style="{ backgroundColor: cat.color }"
          />
          <span :class="hidden.has(cat.key) ? 'line-through' : ''">{{ cat.label }}</span>
          <span v-if="cat.isBlocked" class="opacity-50">(blocked)</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useElementSize } from '@vueuse/core'
import * as d3 from 'd3'
import type { QueuePeriodStat } from '~/purple_client'
import {
  BLOCKED_PALETTE, KIND_LEGACY_COLOR, MAX_BLOCKED, MAX_NOT_BLOCKED, NOT_BLOCKED_PALETTE,
  OTHER_BLOCKED_COLOR, OTHER_NOT_BLOCKED_COLOR, SECONDS_PER_DAY, formatDays, formatWeekRange,
  humanSeconds, isWeekLabel, tooltipPosition, type TooltipPos
} from '~/utils/statsViz'

type Props = {
  periods: QueuePeriodStat[]
  mode: 'total' | 'share'
  dayScale?: number // multiplies day figures (e.g. calendar -> working days)
}
const props = defineProps<Props>()

type Category = {
  key: string
  label: string
  isBlocked: boolean
  isOther: boolean
  members: string[] // role slugs summed into this category
  color: string
}

const root = ref<HTMLElement | null>(null)
const container = ref<HTMLElement | null>(null)
const svgEl = ref<SVGSVGElement | null>(null)
const { width } = useElementSize(container) // reactive container width (VueUse)
const HEIGHT_PX = 340

const MARGIN = { top: 16, right: 16, bottom: 52, left: 64 }
const SEG_GAP_PX = 2 // px of surface between stacked segments (dataviz mark spec)
const CORNER_PX = 4 // px rounded top of each bar

const hidden = reactive(new Set<string>())
function toggle (key: string) {
  if (hidden.has(key)) hidden.delete(key)
  else hidden.add(key)
}

const tooltip = reactive({ visible: false, pos: {} as TooltipPos, title: '', detail: '', members: '' })

const periods = computed(() => props.periods)

// Total seconds per role across all periods, plus its blocked flag.
const roleTotals = computed(() => {
  const totals = new Map<string, { isBlocked: boolean, seconds: number }>()
  for (const p of periods.value) {
    for (const r of p.byRole) {
      const cur = totals.get(r.role) ?? { isBlocked: r.isBlocked, seconds: 0 }
      cur.seconds += r.seconds
      totals.set(r.role, cur)
    }
  }
  return totals
})

// Drawn categories: the top-N roles per polarity keep a distinct color; the
// rest fold into a neutral "Other". Not-blocked (cool) first so blocked (warm)
// reads at the top of each bar.
const categories = computed<Category[]>(() => {
  const nb: { role: string, seconds: number }[] = []
  const bl: { role: string, seconds: number }[] = []
  for (const [role, { isBlocked, seconds }] of roleTotals.value) {
    (isBlocked ? bl : nb).push({ role, seconds })
  }
  nb.sort((a, b) => b.seconds - a.seconds)
  bl.sort((a, b) => b.seconds - a.seconds)

  const out: Category[] = []
  const take = (
    list: { role: string, seconds: number }[], max: number,
    palette: string[], isBlocked: boolean, otherColor: string
  ) => {
    list.slice(0, max).forEach((item, i) => out.push({
      key: item.role, label: item.role, isBlocked, isOther: false,
      members: [item.role], color: palette[i]!
    }))
    const rest = list.slice(max)
    if (rest.length) {
      out.push({
        key: isBlocked ? '__other_blocked' : '__other_not_blocked',
        label: `Other (${rest.length})`,
        isBlocked, isOther: true,
        members: rest.map(r => r.role).sort(),
        color: otherColor
      })
    }
  }
  take(nb, MAX_NOT_BLOCKED, NOT_BLOCKED_PALETTE, false, OTHER_NOT_BLOCKED_COLOR)
  take(bl, MAX_BLOCKED, BLOCKED_PALETTE, true, OTHER_BLOCKED_COLOR)
  return out
})

const visibleCats = computed(() => categories.value.filter(c => !hidden.has(c.key)))

function secondsFor (p: QueuePeriodStat, cat: Category): number {
  return cat.members.reduce(
    (sum, role) => sum + (p.byRole.find(r => r.role === role)?.seconds ?? 0), 0)
}
function visibleSum (p: QueuePeriodStat): number {
  return visibleCats.value.reduce((sum, c) => sum + secondsFor(p, c), 0)
}

/** Path for a rect with only its top two corners rounded. */
function roundedTopRect (x: number, y: number, w: number, h: number, r: number): string {
  const rr = Math.min(r, w / 2, h)
  if (h <= 0) return ''
  return `M${x},${y + h} V${y + rr} Q${x},${y} ${x + rr},${y} H${x + w - rr} Q${x + w},${y} ${x + w},${y + rr} V${y + h} Z`
}

function draw () {
  const svg = d3.select(svgEl.value)
  svg.selectAll('*').remove()
  hideTooltip() // removing a hovered element never fires mouseleave
  if (!svgEl.value || periods.value.length === 0) return

  const data = periods.value
  const cats = visibleCats.value
  // Week ticks carry a second line (the date range), so they need more room.
  const isWeek = isWeekLabel(data[0]?.label)
  const marginBottom = isWeek ? MARGIN.bottom + 16 : MARGIN.bottom
  const innerW = Math.max(width.value - MARGIN.left - MARGIN.right, 10)
  const innerH = HEIGHT_PX - MARGIN.top - marginBottom
  const isShare = props.mode === 'share'
  const dayScale = props.dayScale ?? 1

  const x = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([MARGIN.left, MARGIN.left + innerW])
    .padding(0.25)

  const maxTotal = d3.max(data, d => visibleSum(d)) ?? 0
  const y = d3.scaleLinear()
    .domain([0, isShare ? 1 : (maxTotal === 0 ? 1 : maxTotal)])
    .range([MARGIN.top + innerH, MARGIN.top])
    .nice()

  const yAxis = d3.axisLeft(y).ticks(5).tickFormat(d =>
    isShare ? `${Math.round(Number(d) * 100)}%` : `${Math.round((Number(d) / SECONDS_PER_DAY) * dayScale)}d`)
  const yG = svg.append('g').attr('transform', `translate(${MARGIN.left}, 0)`).call(yAxis)
  yG.selectAll('text').attr('fill', 'currentColor').attr('font-size', 10)
  yG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  const xAxis = d3.axisBottom(x)
  const xG = svg.append('g').attr('transform', `translate(0, ${MARGIN.top + innerH})`).call(xAxis)
  xG.selectAll('text')
    .attr('fill', 'currentColor').attr('font-size', 10)
    .attr('transform', 'rotate(-25)').attr('text-anchor', 'end')
  xG.selectAll('line, path').attr('stroke', 'currentColor').attr('opacity', 0.3)

  // Week labels (2026-W28) are terse; add the covered date range as a 2nd line.
  if (isWeek) {
    xG.selectAll<SVGTextElement, string>('.tick text').each(function (labelValue) {
      const p = data.find(d => d.label === labelValue)
      if (!p) return
      d3.select(this).append('tspan')
        .attr('x', 0).attr('dy', '1.1em').attr('font-size', 8).attr('opacity', 0.7)
        .text(formatWeekRange(p.start, p.end))
    })
  }

  const bandW = x.bandwidth()

  data.forEach(d => {
    const bx = x(d.label) ?? 0
    const denom = visibleSum(d)
    const topCat = [...cats].reverse().find(c => secondsFor(d, c) > 0)
    let cursor = 0 // running total (fraction in share mode, seconds otherwise)
    for (const cat of cats) {
      const secs = secondsFor(d, cat)
      if (secs <= 0) continue
      const val = isShare ? (denom > 0 ? secs / denom : 0) : secs
      if (val <= 0) continue
      const yTop = y(cursor + val)
      const yBottom = y(cursor)
      const h = Math.max(yBottom - yTop - SEG_GAP_PX, 0)
      if (h > 0) {
        const share = denom > 0 ? secs / denom : 0
        const attach = (sel: d3.Selection<never, unknown, null, undefined>) => sel
          .attr('fill', cat.color)
          .style('cursor', 'pointer')
          .on('mousemove', (e: MouseEvent) => showTooltip(e, d, cat, secs, share))
          .on('mouseleave', hideTooltip)
        if (cat === topCat) {
          attach(svg.append('path').attr('d', roundedTopRect(bx, yTop, bandW, h, CORNER_PX)) as never)
        } else {
          attach(svg.append('rect')
            .attr('x', bx).attr('y', yTop)
            .attr('width', bandW).attr('height', h) as never)
        }
      }
      cursor += val
    }

    if (d.legacyIncluded) {
      svg.append('text')
        .attr('x', bx + bandW / 2).attr('y', MARGIN.top + innerH + 2)
        .attr('text-anchor', 'middle').attr('fill', KIND_LEGACY_COLOR).attr('font-size', 8)
        .text('legacy')
    }
  })
}

function showTooltip (event: MouseEvent, d: QueuePeriodStat, cat: Category, seconds: number, share: number) {
  tooltip.pos = tooltipPosition(event, root.value)
  tooltip.visible = true
  const tag = cat.isBlocked ? 'blocked' : 'not blocked'
  const scaled = seconds * (props.dayScale ?? 1)
  tooltip.title = `${d.label} — ${cat.label} (${tag})`
  tooltip.detail = `${formatDays(scaled)} · ${Math.round(share * 100)}% · ${d.docCount} docs · ${humanSeconds(scaled)}`
  tooltip.members = cat.isOther ? cat.members.join(', ') : ''
}

function hideTooltip () {
  tooltip.visible = false
}

// Redraw whenever the data, view mode, container width, or visible categories
// change. useElementSize reports the width after mount (and on resize), which
// drives the first paint — no manual ResizeObserver / lifecycle needed.
watch([periods, width, () => props.mode, () => props.dayScale, visibleCats], () => draw())
</script>
