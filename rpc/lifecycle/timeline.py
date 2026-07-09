# Copyright The IETF Trust 2026, All Rights Reserved
"""Reconstruct time-in-assignment / time-blocked intervals from history.

All data here is derived from django-simple-history records; nothing new is
persisted. Two eras are stitched together at ``TRANSITION_DATE``:

* On/after the transition, "blocked" is an :class:`~rpc.models.Assignment` with
  ``role="blocked"`` and "working" is any other active assignment. Active spans
  are read from each assignment's ``history``.
* Before the transition, old-system states were captured as ``RfcToBe`` labels.
  Those are reconstructed with
  :meth:`~rpc.models.RfcToBe.time_intervals_with_label` and classified as
  blocked-equivalent (holds) or a named legacy state.

Intervals that straddle the boundary are clipped at it so the two eras never
double-count.
"""

import datetime
from dataclasses import dataclass, field
from itertools import pairwise

from django.apps import apps
from django.db import models
from django.utils import timezone

from ..models import (
    ASSIGNMENT_INACTIVE_STATES,
    Assignment,
    Label,
    RfcToBe,
    RfcToBeBlockingReason,
)

# The day the Assignment/Blocked model replaced the old label-based states.
TRANSITION_DATE = datetime.datetime(2026, 5, 20, tzinfo=datetime.UTC)

# Labels that captured old RFC-editor workflow states before the transition.
# Only these labels are reconstructed on the timeline; every other label
# (complexity/type/exception classifications) is a persistent attribute, not a
# time-boxed state.
LEGACY_STATE_LABEL_SLUGS = frozenset(
    {
        "EDIT",
        "REF",
        "RFC-EDITOR",
        "TI",
        "AUTH48-DONE",
        "PENDING",
        "AUTH",
        "AUTH48",
        "IESG",
        "MISSREF",
        "IANA",
    }
)

# The subset of old-editor states that count as "blocked". The remaining
# legacy states (EDIT, REF, RFC-EDITOR, AUTH48-DONE, PENDING) are active work.
LEGACY_BLOCKED_LABEL_SLUGS = frozenset(
    {
        "TI",
        "AUTH",
        "AUTH48",
        "IESG",
        "MISSREF",
        "IANA",
    }
)

# Segment kinds
KIND_BLOCKED = "blocked"
KIND_WORKING = "working"
KIND_LEGACY = "legacy_label"

# One active span: (start, end-or-None, state-at-start).
Run = tuple[datetime.datetime, datetime.datetime | None, str | None]


@dataclass
class Segment:
    """A single span of time in one state.

    ``end`` is ``None`` for an ongoing span; callers clamp it to "now" when
    computing durations.
    """

    start: datetime.datetime
    end: datetime.datetime | None
    kind: str
    role: str | None = None
    label: str | None = None
    person_id: int | None = None
    person_name: str | None = None
    state: str | None = None


@dataclass
class Track:
    """All active spans of a single assignment (one Gantt row)."""

    assignment_id: int
    role: str
    person_id: int | None
    person_name: str | None
    is_blocked: bool
    segments: list[Segment] = field(default_factory=list)


@dataclass
class Band:
    """An aggregate lane (blocked / working summary, or one legacy label)."""

    kind: str
    label: str | None
    segments: list[Segment] = field(default_factory=list)


def _clip(
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


def _active_runs(history_records) -> list[Run]:
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


def _merge_intervals(
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


def _person_name(assignment) -> str | None:
    person = assignment.person
    if person is None or person.datatracker_person is None:
        return None
    return person.datatracker_person.plain_name


def _labels_ever_applied(rfc: RfcToBe) -> set[int]:
    """Primary keys of every label ever applied to ``rfc`` (from history)."""
    pks: set[int] = set()
    hist = list(rfc.history.all())
    for newer, older in pairwise(hist):
        diff = newer.diff_against(older, included_fields=["labels"])
        for change in diff.changes:
            pks.update(related["label"] for related in change.new)
            pks.update(related["label"] for related in change.old)
    return pks


def _assignment_segments(
    rfc: RfcToBe,
) -> list[tuple[Assignment, bool, list[Run]]]:
    """(assignment, is_blocked, clipped active runs) for each assignment.

    Does no person-name lookup (which can hit the datatracker), so it is safe
    to call in bulk from the queue rollup.
    """
    result = []
    assignments = rfc.assignment_set.select_related("role").order_by("id")
    for assignment in assignments:
        history = list(assignment.history.all().order_by("history_date"))
        if not history:
            continue
        runs = []
        for start, end, state in _active_runs(history):
            clipped = _clip(start, end, lo=TRANSITION_DATE)
            if clipped is not None:
                runs.append((clipped[0], clipped[1], state))
        if runs:
            result.append((assignment, assignment.role_id == "blocked", runs))
    return result


def assignment_tracks(rfc: RfcToBe) -> list[Track]:
    """Per-assignment Gantt rows for the post-transition era.

    Resolves ``person_name`` (may hit the datatracker) for display, so this is
    for the single-document view rather than bulk use.
    """
    tracks: list[Track] = []
    for assignment, is_blocked, runs in _assignment_segments(rfc):
        person_name = _person_name(assignment)
        segments = [
            Segment(
                start=start,
                end=end,
                kind=KIND_BLOCKED if is_blocked else KIND_WORKING,
                role=assignment.role_id,
                person_id=assignment.person_id,
                person_name=person_name,
                state=state,
            )
            for start, end, state in runs
        ]
        tracks.append(
            Track(
                assignment_id=assignment.pk,
                role=assignment.role_id,
                person_id=assignment.person_id,
                person_name=person_name,
                is_blocked=is_blocked,
                segments=segments,
            )
        )
    return tracks


def blocked_reason_bands(rfc: RfcToBe, now: datetime.datetime) -> list[Band]:
    """One lane per blocking reason, itemising *why* the doc was blocked.

    Intervals come straight from :class:`~rpc.models.RfcToBeBlockingReason`
    (``since_when`` / ``resolved``) — the same records that drive the queue's
    blocked filter. A reason applied more than once yields one lane with several
    segments; an unresolved reason stays open-ended (``end=None``). Lanes are
    ordered longest-blocking first.
    """
    by_reason: dict[str, tuple[str, list[Segment]]] = {}
    rows = (
        RfcToBeBlockingReason.objects.filter(rfc_to_be=rfc)
        .select_related("reason")
        .order_by("since_when")
    )
    for row in rows:
        _label, segments = by_reason.setdefault(row.reason_id, (row.reason.name, []))
        segments.append(
            Segment(start=row.since_when, end=row.resolved, kind=KIND_BLOCKED)
        )
    bands = [
        Band(kind=KIND_BLOCKED, label=label, segments=segments)
        for label, segments in by_reason.values()
    ]
    bands.sort(
        key=lambda b: sum(
            ((seg.end or now) - seg.start).total_seconds() for seg in b.segments
        ),
        reverse=True,
    )
    return bands


def legacy_bands(rfc: RfcToBe) -> list[Band]:
    """Named legacy-state lanes reconstructed from labels (pre-transition).

    Only the recognized old RFC-editor state labels are reconstructed; other
    labels are persistent classifications, not states, and are ignored.
    """
    label_pks = _labels_ever_applied(rfc)
    if not label_pks:
        return []
    bands: list[Band] = []
    labels = Label.objects.filter(
        pk__in=label_pks, slug__in=LEGACY_STATE_LABEL_SLUGS
    ).order_by("slug")
    for label in labels:
        is_blocked = label.slug in LEGACY_BLOCKED_LABEL_SLUGS
        segments: list[Segment] = []
        for interval in rfc.time_intervals_with_label(label):
            clipped = _clip(interval.start, interval.end, hi=TRANSITION_DATE)
            if clipped is None:
                continue
            segments.append(
                Segment(
                    start=clipped[0],
                    end=clipped[1],
                    kind=KIND_BLOCKED if is_blocked else KIND_LEGACY,
                    label=label.slug,
                )
            )
        if segments:
            bands.append(
                Band(
                    kind=KIND_BLOCKED if is_blocked else KIND_LEGACY,
                    label=label.slug,
                    segments=segments,
                )
            )
    return bands


def document_intervals(
    rfc: RfcToBe, now: datetime.datetime, include_legacy: bool = True
) -> tuple[
    list[tuple[datetime.datetime, datetime.datetime]],
    list[tuple[datetime.datetime, datetime.datetime]],
]:
    """Merged (blocked, working) intervals for a doc across both eras.

    Post-transition intervals come from assignments (clipped to on/after the
    transition); pre-transition intervals come from labels (clipped to before
    it). Blocked-equivalent legacy states fold into blocked; other legacy states
    fold into working.

    ``include_legacy=False`` skips the pre-transition label reconstruction (an
    expensive per-doc history walk); pass it for docs known to have no legacy
    state history, or when no requested window precedes the transition.
    """
    blocked_raw: list[tuple[datetime.datetime, datetime.datetime | None]] = []
    working_raw: list[tuple[datetime.datetime, datetime.datetime | None]] = []

    for _assignment, is_blocked, runs in _assignment_segments(rfc):
        target = blocked_raw if is_blocked else working_raw
        target.extend((start, end) for start, end, _state in runs)

    if include_legacy:
        for band in legacy_bands(rfc):
            target = blocked_raw if band.kind == KIND_BLOCKED else working_raw
            target.extend((seg.start, seg.end) for seg in band.segments)

    return _merge_intervals(blocked_raw, now), _merge_intervals(working_raw, now)


def build_document_timeline(rfc: RfcToBe, now: datetime.datetime | None = None) -> dict:
    """Full per-document timeline payload (tracks + summary + legacy)."""
    now = now or timezone.now()
    # The aggregate "blocked" assignment is itemised per reason below, so drop
    # it from the per-assignment tracks to avoid a redundant lane.
    tracks = [t for t in assignment_tracks(rfc) if t.role != "blocked"]
    blocked_reasons = blocked_reason_bands(rfc, now)
    legacy = legacy_bands(rfc)

    blocked, working = document_intervals(rfc, now)
    summary = [
        Band(
            kind=KIND_WORKING,
            label=None,
            segments=[Segment(start=s, end=e, kind=KIND_WORKING) for s, e in working],
        ),
        Band(
            kind=KIND_BLOCKED,
            label=None,
            segments=[Segment(start=s, end=e, kind=KIND_BLOCKED) for s, e in blocked],
        ),
    ]
    return {
        "transition_date": TRANSITION_DATE,
        "tracks": tracks,
        "summary": summary,
        "blocked_reasons": blocked_reasons,
        "legacy": legacy,
    }


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    """Return ``(year, month)`` shifted by ``delta`` months (month is 1-12)."""
    index = (year * 12 + (month - 1)) + delta
    return index // 12, index % 12 + 1


def _aware(d: datetime.date) -> datetime.datetime:
    return datetime.datetime.combine(d, datetime.time.min, tzinfo=datetime.UTC)


def period_windows(period: str, count: int, now: datetime.datetime) -> list[dict]:
    """Calendar-aligned windows, oldest first, ending with the current period.

    ``period`` is one of ``week`` / ``month`` / ``quarter`` / ``year``.
    """
    if count < 1:
        return []
    today = now.date()
    windows: list[dict] = []

    if period == "year":
        for i in reversed(range(count)):
            y = today.year - i
            windows.append((str(y), datetime.date(y, 1, 1), datetime.date(y + 1, 1, 1)))
    elif period == "quarter":
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        for i in reversed(range(count)):
            y, m = _add_months(today.year, q_start_month, -3 * i)
            ey, em = _add_months(y, m, 3)
            quarter = (m - 1) // 3 + 1
            windows.append(
                (f"{y} Q{quarter}", datetime.date(y, m, 1), datetime.date(ey, em, 1))
            )
    elif period == "month":
        for i in reversed(range(count)):
            y, m = _add_months(today.year, today.month, -i)
            ey, em = _add_months(y, m, 1)
            windows.append(
                (f"{y}-{m:02d}", datetime.date(y, m, 1), datetime.date(ey, em, 1))
            )
    elif period == "week":
        monday = today - datetime.timedelta(days=today.weekday())
        for i in reversed(range(count)):
            start = monday - datetime.timedelta(weeks=i)
            end = start + datetime.timedelta(days=7)
            iso = start.isocalendar()
            windows.append((f"{iso.year}-W{iso.week:02d}", start, end))
    else:
        raise ValueError(f"Unknown period: {period!r}")

    return [
        {"label": label, "start": _aware(start), "end": _aware(end)}
        for label, start, end in windows
    ]


def _overlap_seconds(
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


def _legacy_state_doc_ids(candidate_ids: list[int]) -> set[int]:
    """Subset of ``candidate_ids`` that ever carried a legacy state label.

    Read straight from the historical m2m table, so we only pay the expensive
    per-doc history walk for docs that actually have legacy state history.
    """
    historical_labels = apps.get_model("rpc", "HistoricalRfcToBeLabel")
    return set(
        historical_labels.objects.filter(
            label__slug__in=LEGACY_STATE_LABEL_SLUGS,
            rfctobe_id__in=candidate_ids,
        )
        .values_list("rfctobe_id", flat=True)
        .distinct()
    )


def _candidate_docs(earliest: datetime.datetime, include_legacy: bool):
    """Docs that could contribute time to windows starting at ``earliest``.

    Excludes withdrawn docs and docs published before the range (their time is
    all in the past). Keeps only docs that can produce intervals: those with an
    assignment, or — when legacy matters — those that ever held a state label.
    """
    docs = RfcToBe.objects.exclude(disposition_id="withdrawn").filter(
        models.Q(published_at__isnull=True) | models.Q(published_at__gte=earliest)
    )
    contributes = models.Q(assignment__isnull=False)
    if include_legacy:
        historical_labels = apps.get_model("rpc", "HistoricalRfcToBeLabel")
        ever_state = historical_labels.objects.filter(
            label__slug__in=LEGACY_STATE_LABEL_SLUGS
        ).values("rfctobe_id")
        contributes |= models.Q(pk__in=ever_state)
    return docs.filter(contributes).distinct()


def document_category_intervals(
    rfc: RfcToBe, now: datetime.datetime, include_legacy: bool = True
) -> dict[str, tuple[bool, list[tuple[datetime.datetime, datetime.datetime]]]]:
    """Map each assignment role / legacy state to its merged active intervals.

    Returns ``{category: (is_blocked, merged_intervals)}`` where ``category`` is
    an assignment role slug (post-transition) or a legacy state label slug
    (pre-transition). Open-ended spans are closed at ``now``; callers clip them
    to a period window via :func:`_overlap_seconds`.
    """
    raw: dict[str, tuple[bool, list]] = {}
    for assignment, is_blocked, runs in _assignment_segments(rfc):
        _blocked, intervals = raw.setdefault(assignment.role_id, (is_blocked, []))
        intervals.extend((start, end) for start, end, _state in runs)
    if include_legacy:
        for band in legacy_bands(rfc):
            is_blocked = band.kind == KIND_BLOCKED
            _blocked, intervals = raw.setdefault(band.label, (is_blocked, []))
            intervals.extend((seg.start, seg.end) for seg in band.segments)
    return {
        category: (is_blocked, _merge_intervals(intervals, now))
        for category, (is_blocked, intervals) in raw.items()
    }


def queue_rollup(
    period: str, count: int, now: datetime.datetime | None = None
) -> list[dict]:
    """Per-period assignment-time breakdown for the queue.

    Each period (bin) reports on the documents that were in the queue during the
    period: those in the queue by the end of the period (the current period ends
    "now" — year-to-date, etc.) that had not left before it started. For those
    documents it sums the time spent in each assignment role — and pre-transition
    legacy states — *within* the period, with aggregate blocked / not-blocked
    totals. Time is a per-period flow, not a running cumulative total, so a
    document that sits in one state for months contributes only that period's
    share to each bin (rather than an ever-growing total).

    Withdrawn docs and docs published before the requested range are excluded.
    """
    now = now or timezone.now()
    windows = period_windows(period, count, now)
    if not windows:
        return []

    earliest = windows[0]["start"]
    include_legacy = earliest < TRANSITION_DATE

    docs = list(_candidate_docs(earliest, include_legacy).with_enqueued_at())
    legacy_ids = (
        _legacy_state_doc_ids([d.pk for d in docs]) if include_legacy else set()
    )
    doc_data = [
        (
            rfc.enqueued_at,
            rfc.published_at,
            document_category_intervals(rfc, now, include_legacy=rfc.pk in legacy_ids),
        )
        for rfc in docs
    ]

    periods: list[dict] = []
    for window in windows:
        start = window["start"]
        # The current (rightmost) period ends "now", not at its calendar edge.
        eff_end = min(window["end"], now)

        role_totals: dict[str, list] = {}  # role -> [is_blocked, seconds]
        blocked_total = 0.0
        working_total = 0.0
        member_count = 0

        for enqueued, published, categories in doc_data:
            # Bin membership: existed by the period end, and had not left the
            # queue before the period started.
            if enqueued is not None and enqueued > eff_end:
                continue
            if published is not None and published < start:
                continue
            member_count += 1
            for role, (is_blocked, intervals) in categories.items():
                # Per-period flow: only the portion of each interval that falls
                # within this window, so long-running states (e.g. MISSREF, EDIT)
                # do not accumulate into an ever-growing cumulative total.
                seconds = _overlap_seconds(intervals, start, eff_end)
                if seconds <= 0:
                    continue
                slot = role_totals.setdefault(role, [is_blocked, 0.0])
                slot[1] += seconds
                if is_blocked:
                    blocked_total += seconds
                else:
                    working_total += seconds

        by_role = [
            {"role": role, "is_blocked": is_blocked, "seconds": seconds}
            for role, (is_blocked, seconds) in sorted(
                role_totals.items(), key=lambda item: item[1][1], reverse=True
            )
        ]
        periods.append(
            {
                "label": window["label"],
                "start": window["start"],
                "end": window["end"],
                "doc_count": member_count,
                "total_blocked_seconds": blocked_total,
                "total_working_seconds": working_total,
                "by_role": by_role,
                "legacy_included": start < TRANSITION_DATE,
            }
        )
    return periods
