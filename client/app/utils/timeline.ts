import humanizeDuration from 'humanize-duration'
import type { TimelineSegment } from '~/purple_client'

// Segment kinds emitted by the backend (rpc.lifecycle.timeline).
export const KIND_BLOCKED = 'blocked'
export const KIND_WORKING = 'working'
export const KIND_LEGACY = 'legacy_label'
export const KIND_AWAITING = 'awaiting_ref'

// Shared colors so the doc timeline and queue summary read as one system:
// these match the lead hues of the per-role palettes below (blocked = warm red,
// working = cool teal) plus a violet for the legacy / transition motif. All
// three pass the dataviz validator on both the light (#fff) and dark (#000)
// card surfaces.
export const KIND_LEGACY_COLOR = '#7c3aed' // violet-600 (legacy states + transition marker)
export const KIND_COLORS: Record<string, string> = {
  [KIND_BLOCKED]: '#dc2626', // red-600   — matches BLOCKED_PALETTE[0]
  [KIND_WORKING]: '#0d9488', // teal-600  — matches NOT_BLOCKED_PALETTE[0]
  [KIND_AWAITING]: '#b45309', // amber-700 — waiting on a reference (final review)
  [KIND_LEGACY]: KIND_LEGACY_COLOR
}

export const KIND_LABELS: Record<string, string> = {
  [KIND_BLOCKED]: 'Blocked',
  [KIND_WORKING]: 'Not blocked',
  [KIND_AWAITING]: 'Awaiting ref',
  [KIND_LEGACY]: 'Legacy state'
}

export function kindColor (kind: string): string {
  return KIND_COLORS[kind] ?? KIND_COLORS[KIND_LEGACY]!
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
  const days = Math.round(seconds / 86400)
  return days === 0 ? '<1d' : `${days}d`
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

/**
 * Assign a stable color to each role. Not-blocked roles come first (cool),
 * blocked roles last (warm); returns the ordered role list and a color lookup.
 */
export function roleColorScale (
  roles: { role: string, isBlocked: boolean }[]
): { ordered: string[], colorOf: (role: string) => string } {
  const notBlocked = roles.filter(r => !r.isBlocked).map(r => r.role).sort()
  const blocked = roles.filter(r => r.isBlocked).map(r => r.role).sort()
  const colors: Record<string, string> = {}
  notBlocked.forEach((role, i) => {
    colors[role] = NOT_BLOCKED_PALETTE[i % NOT_BLOCKED_PALETTE.length]!
  })
  blocked.forEach((role, i) => {
    colors[role] = BLOCKED_PALETTE[i % BLOCKED_PALETTE.length]!
  })
  return {
    ordered: [...notBlocked, ...blocked],
    colorOf: (role: string) => colors[role] ?? KIND_COLORS[KIND_LEGACY]!
  }
}
