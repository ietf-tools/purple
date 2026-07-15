import humanizeDuration from 'humanize-duration'
import { DateTime } from 'luxon'
import type { TimelineSegment } from '~/purple_client'

export const SECONDS_PER_DAY = 86_400
export const MS_PER_DAY = 86_400_000

// Segment kinds emitted by the backend (rpc.lifecycle.timeline). These mirror
// the KIND_* values in rpc/lifecycle/timeline.py; there is no generated enum for
// them, so this is a small hand-kept copy of that contract.
export const KIND_BLOCKED = 'blocked'
export const KIND_WORKING = 'working'
export const KIND_LEGACY = 'legacy_label'
export const KIND_AWAITING = 'awaiting_ref'

/** The set of segment kinds, as a narrow type for keying the maps below. */
export type Kind =
  | typeof KIND_BLOCKED
  | typeof KIND_WORKING
  | typeof KIND_LEGACY
  | typeof KIND_AWAITING

// Shared colors so the doc timeline and queue summary read as one system:
// these match the lead hues of the per-role palettes below (blocked = warm red,
// working = cool teal) plus a violet for the legacy / transition motif. All
// three pass the dataviz validator on both the light (#fff) and dark (#000)
// card surfaces.
export const KIND_LEGACY_COLOR = '#7c3aed' // violet-600 (legacy states + transition marker)
export const KIND_COLORS: Record<Kind, string> = {
  [KIND_BLOCKED]: '#dc2626', // red-600   — matches BLOCKED_PALETTE[0]
  [KIND_WORKING]: '#0d9488', // teal-600  — matches NOT_BLOCKED_PALETTE[0]
  [KIND_AWAITING]: '#b45309', // amber-700 — waiting on a reference (final review)
  [KIND_LEGACY]: KIND_LEGACY_COLOR
}

export const KIND_LABELS: Record<Kind, string> = {
  [KIND_BLOCKED]: 'Blocked',
  [KIND_WORKING]: 'Not blocked',
  [KIND_AWAITING]: 'Awaiting ref',
  [KIND_LEGACY]: 'Legacy state'
}

/** Color for a backend-supplied kind string (falls back to the legacy hue). */
export function kindColor (kind: string): string {
  return KIND_COLORS[kind as Kind] ?? KIND_LEGACY_COLOR
}

/** Display label for a backend-supplied kind string (falls back to the raw kind). */
export function kindLabel (kind: string): string {
  return KIND_LABELS[kind as Kind] ?? kind
}

/** Segment end, defaulting an open-ended (ongoing) segment to `now`. */
export function segmentEnd (segment: TimelineSegment, now: Date = new Date()): Date {
  return segment.end ?? now
}

/** Duration of a segment in milliseconds (open-ended clamped to `now`). */
export function segmentMillis (segment: TimelineSegment, now: Date = new Date()): number {
  return segmentEnd(segment, now).getTime() - segment.start.getTime()
}

/** Total milliseconds across a set of segments. */
export function totalMillis (segments: TimelineSegment[], now: Date = new Date()): number {
  return segments.reduce((sum, s) => sum + segmentMillis(s, now), 0)
}

const humanize = humanizeDuration.humanizer({
  largest: 2,
  round: true,
  units: ['y', 'mo', 'd', 'h', 'm']
})

/** Human-readable duration from milliseconds, e.g. "3 days, 4 hours". */
export function humanMillis (ms: number): string {
  if (ms <= 0) {
    return '0'
  }
  return humanize(ms)
}

/** Human-readable duration from seconds (backend stats are in seconds). */
export function humanSeconds (seconds: number): string {
  return humanMillis(seconds * 1000)
}

/** Whole-day rendering for the queue summary (never sub-day units). */
export function formatDays (seconds: number): string {
  if (seconds <= 0) {
    return '—'
  }
  const days = Math.round(seconds / SECONDS_PER_DAY)
  return days === 0 ? '<1d' : `${days}d`
}

// Week period labels look like "2026-W28"; the stats tables/chart show the
// covered date range beneath them.
const WEEK_LABEL_RE = /^\d{4}-W\d{2}$/

/** True if a period label is an ISO-week label (e.g. "2026-W28"). */
export function isWeekLabel (label: string | undefined): boolean {
  return WEEK_LABEL_RE.test(label ?? '')
}

/**
 * Human date range covered by a week window, e.g. "Jul 6 – Jul 12". `end` is
 * exclusive (the next Monday), so the last day shown is `end - 1 day`. Formatted
 * in UTC to match the UTC-midnight window boundaries.
 */
export function formatWeekRange (start: Date, end: Date): string {
  const fmt = (d: Date) =>
    DateTime.fromJSDate(d, { zone: 'utc' }).toLocaleString({ month: 'short', day: 'numeric' })
  return `${fmt(start)} – ${fmt(new Date(end.getTime() - MS_PER_DAY))}`
}

// Palettes for per-role stacking: cool hues for not-blocked roles, warm hues
// for blocked roles, so the blocked share of each bar reads at a glance. Both
// pass the dataviz validator (lightness band, chroma, adjacent-CVD, contrast)
// against the app's light (#fff) AND dark (#000) card surfaces, so one palette
// serves both themes. Each family is capped at the number of CVD-distinct hues
// it supports (cool 7, warm 4); roles beyond the cap fold into a neutral
// "Other" bucket (see MAX_* / OTHER_* below and StackedTimeBars).
export const NOT_BLOCKED_PALETTE = [
  '#0d9488', '#0284c7', '#16a34a', '#4f46e5', '#0891b2', '#65a30d', '#2563eb'
] // cool hues for not-blocked roles
export const BLOCKED_PALETTE = ['#dc2626', '#ea580c', '#e11d48', '#a16207'] // warm hues for blocked roles
export const MAX_NOT_BLOCKED = NOT_BLOCKED_PALETTE.length
export const MAX_BLOCKED = BLOCKED_PALETTE.length
export const OTHER_NOT_BLOCKED_COLOR = '#64748b' // slate-500 (neutral, cool)
export const OTHER_BLOCKED_COLOR = '#78716c' // stone-500 (neutral, warm)

// Colors for the RFC-status buckets on the Stream tab (one categorical
// dimension). Drawn from the same validator-clean palette; Historic is warm
// amber and Unknown a neutral slate so they read as "other". Fallback slate.
export const PUBLISHED_STATUS_COLORS: Record<string, string> = {
  'Standards Track': '#0284c7',
  'Best Current Practice': '#0d9488',
  Experimental: '#4f46e5',
  Informational: '#16a34a',
  Historic: '#a16207',
  Unknown: '#64748b'
}
export function statusColor (status: string): string {
  return PUBLISHED_STATUS_COLORS[status] ?? '#64748b'
}

/**
 * Ordered union of roles for the summary table: not-blocked first, then
 * blocked, each alphabetical. (The chart colors/orders its own bars by total;
 * this ordering is just for the table's columns.)
 */
export function orderedRoles (
  roles: { role: string, isBlocked: boolean }[]
): string[] {
  const notBlocked = roles.filter(r => !r.isBlocked).map(r => r.role).sort()
  const blocked = roles.filter(r => r.isBlocked).map(r => r.role).sort()
  return [...notBlocked, ...blocked]
}
