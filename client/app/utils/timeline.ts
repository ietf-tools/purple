import humanizeDuration from 'humanize-duration'
import type { TimelineSegment } from '~/purple_client'

// Segment kinds emitted by the backend (rpc.lifecycle.timeline).
export const KIND_BLOCKED = 'blocked'
export const KIND_WORKING = 'working'
export const KIND_LEGACY = 'legacy_label'

// Shared colors so the doc timeline and queue summary read as one system.
// Blocked = warm/red, working = teal/green, legacy = neutral violet.
export const KIND_COLORS: Record<string, string> = {
  [KIND_BLOCKED]: '#ef4444', // red-500
  [KIND_WORKING]: '#14b8a6', // teal-500
  [KIND_LEGACY]: '#a78bfa' // violet-400
}

export const KIND_LABELS: Record<string, string> = {
  [KIND_BLOCKED]: 'Blocked',
  [KIND_WORKING]: 'Not blocked',
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
// for blocked roles, so the blocked share of each bar reads at a glance.
const NOT_BLOCKED_PALETTE = [
  '#14b8a6', '#0ea5e9', '#22c55e', '#6366f1', '#06b6d4', '#84cc16', '#3b82f6', '#8b5cf6'
]
const BLOCKED_PALETTE = ['#ef4444', '#f97316', '#e11d48', '#f59e0b', '#dc2626', '#b91c1c']

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
