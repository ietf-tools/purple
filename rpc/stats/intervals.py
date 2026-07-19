# Copyright The IETF Trust 2026, All Rights Reserved
"""Interval algebra shared by the per-document timeline and the queue rollups.

Half-open ``[start, end)`` spans are ``(datetime, datetime | None)`` tuples,
where ``None`` means still open. The public functions here are the API consumed
by :mod:`rpc.stats.timeline` and :mod:`rpc.stats.rollups`; module-private
helpers keep the ``_`` prefix.

Everything is generic set algebra over spans except :func:`active_runs`, the one
assignment-aware entry point: it collapses an ordered stream of assignment
history records into active spans using ``ASSIGNMENT_INACTIVE_STATES`` (the only
database-derived value this module references).
"""

import datetime

from ..models import ASSIGNMENT_INACTIVE_STATES

# One active span: (start, end-or-None, state-at-start).
Run = tuple[datetime.datetime, datetime.datetime | None, str | None]


def clip(
    start: datetime.datetime,
    end: datetime.datetime | None,
    lo: datetime.datetime | None = None,
    hi: datetime.datetime | None = None,
) -> tuple[datetime.datetime, datetime.datetime | None] | None:
    """Clip ``[start, end)`` to ``[lo, hi)``; return ``None`` if empty.

    An open-ended span (``end is None``) stays open unless ``hi`` closes it.
    """
    if lo is not None and start < lo:
        start = lo
    if hi is not None and (end is None or end > hi):
        end = hi
    if end is not None and start >= end:
        return None
    return start, end


def active_runs(history_records) -> list[Run]:
    """Return ``(start, end, state_at_start)`` for each contiguous active span.

    ``history_records`` must be ordered oldest-first. ``end`` is ``None`` for a
    span that is still active.
    """
    runs: list[Run] = []
    run_start: datetime.datetime | None = None
    run_state: str | None = None
    for rec in history_records:
        is_active = rec.state not in ASSIGNMENT_INACTIVE_STATES
        if is_active and run_start is None:
            run_start = rec.history_date
            run_state = rec.state
        elif not is_active and run_start is not None:
            runs.append((run_start, rec.history_date, run_state))
            run_start = None
            run_state = None
    if run_start is not None:
        runs.append((run_start, None, run_state))
    return runs


def merge_intervals(
    intervals: list[tuple[datetime.datetime, datetime.datetime | None]],
    now: datetime.datetime,
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """Union overlapping/adjacent intervals; open ends are clamped to ``now``."""
    norm = sorted(
        ((s, e if e is not None else now) for s, e in intervals),
        key=lambda pair: pair[0],
    )
    merged: list[tuple[datetime.datetime, datetime.datetime]] = []
    for start, end in norm:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def split_runs_by_intervals(
    runs: list[Run],
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    now: datetime.datetime,
) -> tuple[list[tuple], list[tuple]]:
    """Partition ``runs`` into (inside-intervals, outside-intervals) spans.

    ``intervals`` must be sorted and non-overlapping (as from merge_intervals).
    Open-ended runs are treated as ending ``now``.
    """
    inside: list[tuple] = []
    outside: list[tuple] = []
    for start, end, _state in runs:
        run_end = end or now
        cursor = start
        for a_start, a_end in intervals:
            lo, hi = max(start, a_start), min(run_end, a_end)
            if hi <= lo:
                continue
            if lo > cursor:
                outside.append((cursor, lo))
            inside.append((lo, hi))
            cursor = hi
        if run_end > cursor:
            outside.append((cursor, run_end))
    return inside, outside


def subtract_intervals(
    base: list[tuple[datetime.datetime, datetime.datetime]],
    cuts: list[tuple[datetime.datetime, datetime.datetime]],
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """``base`` minus ``cuts``; both merged, sorted, closed intervals."""
    result: list[tuple[datetime.datetime, datetime.datetime]] = []
    for b_start, b_end in base:
        cursor = b_start
        for c_start, c_end in cuts:
            if c_end <= cursor or c_start >= b_end:
                continue
            if c_start > cursor:
                result.append((cursor, c_start))
            cursor = max(cursor, c_end)
            if cursor >= b_end:
                break
        if cursor < b_end:
            result.append((cursor, b_end))
    return result


def intersect_intervals(
    a: list[tuple[datetime.datetime, datetime.datetime]],
    b: list[tuple[datetime.datetime, datetime.datetime]],
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """``a`` ∩ ``b`` (both merged, sorted, closed): ``a`` minus (``a`` minus ``b``)."""
    return subtract_intervals(a, subtract_intervals(a, b))


def overlap_seconds(
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    window_start: datetime.datetime,
    window_end: datetime.datetime,
) -> float:
    total = 0.0
    for start, end in intervals:
        lo = max(start, window_start)
        hi = min(end, window_end)
        if hi > lo:
            total += (hi - lo).total_seconds()
    return total


def covered_at(
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    when: datetime.datetime,
) -> bool:
    """True if ``when`` falls within any of the (non-overlapping) intervals."""
    return any(start <= when <= end for start, end in intervals)


def _merge_open_intervals(
    intervals: list[tuple[datetime.datetime, datetime.datetime | None]],
) -> list[tuple[datetime.datetime, datetime.datetime | None]]:
    """Merge overlapping intervals; an ``end`` of ``None`` means still open."""
    merged: list[tuple[datetime.datetime, datetime.datetime | None]] = []
    for start, end in sorted(intervals, key=lambda p: p[0]):
        if merged:
            prev_start, prev_end = merged[-1]
            if prev_end is None or start <= prev_end:
                merged[-1] = (
                    prev_start,
                    None if (prev_end is None or end is None) else max(prev_end, end),
                )
                continue
        merged.append((start, end))
    return merged


def first_clear_after(
    intervals: list[tuple[datetime.datetime, datetime.datetime | None]],
    since: datetime.datetime,
) -> datetime.datetime | None:
    """First instant >= ``since`` not covered by any interval (None if never)."""
    for start, end in _merge_open_intervals(intervals):
        if start <= since and (end is None or since < end):
            return end  # inside a covering interval; clears at its end (None=never)
        if start > since:
            break  # the next interval is later, so ``since`` is already clear
    return since
