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

from ..dt_v1_api_utils import datatracker_ietf_meetings
from ..models import (
    ASSIGNMENT_INACTIVE_STATES,
    Assignment,
    DocRelationshipName,
    Label,
    RfcToBe,
    RfcToBeBlockingReason,
    RpcRelatedDocument,
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
KIND_AWAITING = "awaiting_ref"

# Manually-applied labels flagging a final-review doc that is waiting on a
# referenced RFC-to-be. Only ever set while in the final_review_editor state.
AWAITING_REF_LABEL_PREFIX = "awaiting ref:"

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


def _awaiting_ref_intervals(
    rfc: RfcToBe, now: datetime.datetime
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """Merged intervals during which any ``awaiting ref:`` label was applied.

    These labels are manually applied only while a doc is in final review; the
    union of their applied intervals marks the "awaiting a reference" time.
    """
    label_pks = _labels_ever_applied(rfc)
    if not label_pks:
        return []
    labels = Label.objects.filter(pk__in=label_pks).filter(
        slug__istartswith=AWAITING_REF_LABEL_PREFIX
    )
    raw: list[tuple[datetime.datetime, datetime.datetime | None]] = []
    for label in labels:
        for interval in rfc.time_intervals_with_label(label):
            raw.append((interval.start, interval.end))
    return _merge_intervals(raw, now) if raw else []


def _split_runs_by_intervals(
    runs: list[Run],
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    now: datetime.datetime,
) -> tuple[list[tuple], list[tuple]]:
    """Partition ``runs`` into (inside-intervals, outside-intervals) spans.

    ``intervals`` must be sorted and non-overlapping (as from _merge_intervals).
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


def _make_track(assignment, person_name: str | None, is_blocked: bool, segments):
    return Track(
        assignment_id=assignment.pk,
        role=assignment.role_id,
        person_id=assignment.person_id,
        person_name=person_name,
        is_blocked=is_blocked,
        segments=segments,
    )


def _spans_to_segments(spans, kind, assignment, person_name, now):
    """Build display segments from bare (start, end) spans; end==now -> ongoing."""
    return [
        Segment(
            start=s,
            end=None if e == now else e,
            kind=kind,
            role=assignment.role_id,
            person_id=assignment.person_id,
            person_name=person_name,
        )
        for s, e in spans
    ]


def assignment_tracks(
    rfc: RfcToBe, now: datetime.datetime | None = None
) -> list[Track]:
    """Per-assignment Gantt rows for the post-transition era.

    Resolves ``person_name`` (may hit the datatracker) for display, so this is
    for the single-document view rather than bulk use. A ``final_review_editor``
    assignment is split into a "not awaiting ref" (working) row and an
    "awaiting ref" row wherever an ``awaiting ref:`` label was applied.
    """
    now = now or timezone.now()
    awaiting = _awaiting_ref_intervals(rfc, now)
    tracks: list[Track] = []
    for assignment, is_blocked, runs in _assignment_segments(rfc):
        person_name = _person_name(assignment)
        if assignment.role_id == "final_review_editor" and awaiting:
            inside, outside = _split_runs_by_intervals(runs, awaiting, now)
            if outside:
                segs = _spans_to_segments(
                    outside, KIND_WORKING, assignment, person_name, now
                )
                tracks.append(_make_track(assignment, person_name, False, segs))
            if inside:
                # Awaiting-ref time counts as blocked (is_blocked=True); the
                # KIND_AWAITING segments keep their distinct amber colour.
                segs = _spans_to_segments(
                    inside, KIND_AWAITING, assignment, person_name, now
                )
                tracks.append(_make_track(assignment, person_name, True, segs))
        else:
            kind = KIND_BLOCKED if is_blocked else KIND_WORKING
            segments = [
                Segment(
                    start=start,
                    end=end,
                    kind=kind,
                    role=assignment.role_id,
                    person_id=assignment.person_id,
                    person_name=person_name,
                    state=state,
                )
                for start, end, state in runs
            ]
            tracks.append(_make_track(assignment, person_name, is_blocked, segments))
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


def _subtract_intervals(
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
    fold into working. Time with an ``awaiting ref:`` label (applied only during
    final review) counts as blocked, so it is folded into blocked and carved out
    of working.

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

    blocked = _merge_intervals(blocked_raw, now)
    working = _merge_intervals(working_raw, now)
    awaiting = _awaiting_ref_intervals(rfc, now)
    if awaiting:
        blocked = _merge_intervals([*blocked, *awaiting], now)
        working = _subtract_intervals(working, awaiting)
    return blocked, working


def build_document_timeline(rfc: RfcToBe, now: datetime.datetime | None = None) -> dict:
    """Full per-document timeline payload (tracks + summary + legacy)."""
    now = now or timezone.now()
    # The aggregate "blocked" assignment is itemised per reason below, so drop
    # it from the per-assignment tracks to avoid a redundant lane.
    tracks = [t for t in assignment_tracks(rfc, now) if t.role != "blocked"]
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
    """Windows, oldest first, ending with the current period.

    ``period`` is one of ``week`` / ``month`` / ``quarter`` / ``year`` (all
    calendar-aligned) or ``ietf`` (spans between consecutive IETF meetings).
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
    elif period == "ietf":
        # Each period runs between consecutive IETF meetings and is labelled by
        # the meeting it ends at. The current (rightmost) period ends at the
        # nearest meeting in the future, or — if none are scheduled — at the most
        # recent past meeting.
        meetings = datatracker_ietf_meetings()  # (number, date), date ascending
        if len(meetings) < 2:
            return []
        numbers = [number for number, _date in meetings]
        dates = [date for _number, date in meetings]
        cur = next((i for i, d in enumerate(dates) if d >= today), len(dates) - 1)
        first = max(1, cur - count + 1)
        for j in range(first, cur + 1):
            windows.append((f"IETF {numbers[j]}", dates[j - 1], dates[j]))
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


def _covered_at(
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    when: datetime.datetime,
) -> bool:
    """True if ``when`` falls within any of the (non-overlapping) intervals."""
    return any(start <= when <= end for start, end in intervals)


# Enqueue and the not-received relationship that comes in with a doc are written
# in the same (non-atomic) intake, so the relationship's history stamp lands a
# few ms after ``enqueued_at``. Treat a missing-ref interval that starts within
# this window of entry as "present at entry"; a reference discovered later (days)
# is well outside it.
_MISSING_REF_ENTRY_GRACE = datetime.timedelta(minutes=5)

# The legacy (pre-transition) MISSREF label was often applied in a batch some
# days after a doc was enqueued, yet reflects its state at entry. Count a MISSREF
# label appearing within a week of enqueue as "entered the queue missing a ref".
_MISSREF_LABEL_ENTRY_GRACE = datetime.timedelta(weeks=1)


def _missing_ref_at_entry(
    intervals: list[tuple[datetime.datetime, datetime.datetime]],
    enq: datetime.datetime,
    grace: datetime.timedelta,
) -> bool:
    """True if a missing-ref interval covers ``enq`` or starts within ``grace``."""
    return _covered_at(intervals, enq) or any(
        enq <= start <= enq + grace for start, _ in intervals
    )


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


def _awaiting_ref_doc_ids(candidate_ids: list[int]) -> set[int]:
    """Subset of ``candidate_ids`` that ever carried an ``awaiting ref:`` label.

    Read from the historical m2m table so the queue rollup only pays the
    per-doc history walk for docs that actually have such a label.
    """
    historical_labels = apps.get_model("rpc", "HistoricalRfcToBeLabel")
    return set(
        historical_labels.objects.filter(
            label__slug__istartswith=AWAITING_REF_LABEL_PREFIX,
            rfctobe_id__in=candidate_ids,
        )
        .values_list("rfctobe_id", flat=True)
        .distinct()
    )


def _blocked_reason_doc_ids(candidate_ids: list[int]) -> set[int]:
    """Subset of ``candidate_ids`` that have any recorded blocking reason."""
    return set(
        RfcToBeBlockingReason.objects.filter(rfc_to_be_id__in=candidate_ids)
        .values_list("rfc_to_be_id", flat=True)
        .distinct()
    )


def _blocked_reason_intervals(
    rfc: RfcToBe, now: datetime.datetime
) -> dict[str, list[tuple[datetime.datetime, datetime.datetime]]]:
    """Merged blocked intervals keyed by blocking-reason name.

    Same source as the doc timeline's reason lanes (RfcToBeBlockingReason), used
    to itemise the queue's blocked time by reason.
    """
    by_reason: dict[str, list] = {}
    rows = (
        RfcToBeBlockingReason.objects.filter(rfc_to_be=rfc)
        .select_related("reason")
        .order_by("since_when")
    )
    for row in rows:
        by_reason.setdefault(row.reason.name, []).append((row.since_when, row.resolved))
    return {name: _merge_intervals(ivs, now) for name, ivs in by_reason.items()}


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
    rfc: RfcToBe,
    now: datetime.datetime,
    include_legacy: bool = True,
    include_awaiting: bool = False,
    include_reasons: bool = False,
) -> dict[str, tuple[bool, list[tuple[datetime.datetime, datetime.datetime]]]]:
    """Map each assignment role / legacy state to its merged active intervals.

    Returns ``{category: (is_blocked, merged_intervals)}`` where ``category`` is
    an assignment role slug (post-transition) or a legacy state label slug
    (pre-transition). Open-ended spans are closed at ``now``; callers clip them
    to a period window via :func:`_overlap_seconds`.

    ``include_awaiting`` carves ``awaiting ref:`` time out of the
    ``final_review_editor`` category into a blocked ``awaiting_ref`` category, so
    that time counts as blocked (pass it only for docs known to have such a
    label — see :func:`_awaiting_ref_doc_ids`).

    ``include_reasons`` replaces the single ``blocked`` category with one blocked
    category per blocking reason (by name), mirroring the doc timeline
    (pass it only for docs known to have reasons — see
    :func:`_blocked_reason_doc_ids`).
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
    result = {
        category: (is_blocked, _merge_intervals(intervals, now))
        for category, (is_blocked, intervals) in raw.items()
    }
    if include_awaiting:
        awaiting = _awaiting_ref_intervals(rfc, now)
        if awaiting:
            fre = result.get("final_review_editor")
            if fre is not None:
                result["final_review_editor"] = (
                    fre[0], _subtract_intervals(fre[1], awaiting)
                )
            result["awaiting_ref"] = (True, awaiting)
    if include_reasons:
        reasons = _blocked_reason_intervals(rfc, now)
        if reasons:
            result.pop("blocked", None)  # itemised per reason below
            for name, intervals in reasons.items():
                result[name] = (True, intervals)
    return result


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
    doc_ids = [d.pk for d in docs]
    legacy_ids = _legacy_state_doc_ids(doc_ids) if include_legacy else set()
    awaiting_ids = _awaiting_ref_doc_ids(doc_ids)
    reason_ids = _blocked_reason_doc_ids(doc_ids)
    doc_data = [
        (
            rfc.enqueued_at,
            rfc.published_at,
            document_category_intervals(
                rfc,
                now,
                include_legacy=rfc.pk in legacy_ids,
                include_awaiting=rfc.pk in awaiting_ids,
                include_reasons=rfc.pk in reason_ids,
            ),
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


def _blocked_doc_ids(candidate_ids: list[int]) -> set[int]:
    """Docs ever blocked (blocked assignment, blocking reason, or a legacy
    blocked-state label) — the only ones needing a blocked-interval walk."""
    ids = set(
        Assignment.objects.filter(
            rfc_to_be_id__in=candidate_ids, role__slug="blocked"
        ).values_list("rfc_to_be_id", flat=True)
    )
    ids |= set(
        RfcToBeBlockingReason.objects.filter(
            rfc_to_be_id__in=candidate_ids
        ).values_list("rfc_to_be_id", flat=True)
    )
    historical_labels = apps.get_model("rpc", "HistoricalRfcToBeLabel")
    ids |= set(
        historical_labels.objects.filter(
            label__slug__in=LEGACY_BLOCKED_LABEL_SLUGS, rfctobe_id__in=candidate_ids
        ).values_list("rfctobe_id", flat=True)
    )
    return ids


def _pages_at(rfc_pk: int, when: datetime.datetime | None) -> int:
    """The doc's ``pages`` from the history record in effect at ``when``."""
    if when is None:
        return 0
    historical = RfcToBe.history.model
    pages = (
        historical.objects.filter(id=rfc_pk, history_date__lte=when)
        .order_by("-history_date")
        .values_list("pages", flat=True)
        .first()
    )
    return pages or 0


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


def _first_clear_after(
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


def _missing_ref_intervals_by_doc(
    doc_ids: list[int],
) -> dict[int, list[tuple[datetime.datetime, datetime.datetime | None]]]:
    """Per-doc intervals during which a not-received reference existed.

    Reconstructed from :class:`~rpc.models.RpcRelatedDocument` history: each
    not-received (1g/2g/3g) relationship contributes ``[created, deleted)``.
    """
    historical = RpcRelatedDocument.history.model
    # source -> relationship-row-id -> {"start", "end"}
    by_doc: dict[int, dict[int, dict]] = {}
    rows = (
        historical.objects.filter(
            source_id__in=doc_ids,
            relationship__slug__in=DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUGS,
        )
        .order_by("history_date")
        .values("id", "source_id", "history_type", "history_date")
    )
    for row in rows:
        rel = by_doc.setdefault(row["source_id"], {}).setdefault(
            row["id"], {"start": None, "end": None}
        )
        if row["history_type"] == "+" and rel["start"] is None:
            rel["start"] = row["history_date"]
        elif row["history_type"] == "-":
            rel["end"] = row["history_date"]
    return {
        source_id: [
            (rel["start"], rel["end"])
            for rel in rels.values()
            if rel["start"] is not None
        ]
        for source_id, rels in by_doc.items()
    }


def queue_counts_rollup(
    period: str, count: int, now: datetime.datetime | None = None
) -> list[dict]:
    """Per-period document/page counts for the queue.

    Each period reports: docs in queue at the start; docs and pages entering
    during the period; RFCs published; pages "gone to edit" (a doc reaches no
    missing references for the first time since entering the queue); docs blocked
    the entire period; and the average blocked share of the rest (docs that could
    be worked on). "Missing references" = an active not-received (1g/2g/3g)
    reference relationship, or — before the transition — the legacy MISSREF
    state. Page counts are read from the ``pages`` in the doc's history record in
    effect when it entered / went to edit. Blocked time is the same union used by
    the time view; "% time blocked" is over the time a doc was in the queue
    during the period.
    """
    now = now or timezone.now()
    windows = period_windows(period, count, now)
    if not windows:
        return []
    earliest = windows[0]["start"]

    docs = list(
        RfcToBe.objects.exclude(disposition_id="withdrawn")
        .filter(
            models.Q(published_at__isnull=True) | models.Q(published_at__gte=earliest)
        )
        .with_enqueued_at()
        .values("pk", "published_at", "enqueued_at")
    )
    doc_ids = [d["pk"] for d in docs]

    # "Gone to edit" = first time with no missing references since enqueue.
    # Missing references = not-received relationships (any era) + legacy MISSREF.
    notrecv = _missing_ref_intervals_by_doc(doc_ids)
    missref_label = Label.objects.filter(slug="MISSREF").first()
    missref_ids = (
        set(
            apps.get_model("rpc", "HistoricalRfcToBeLabel")
            .objects.filter(label__slug="MISSREF", rfctobe_id__in=doc_ids)
            .values_list("rfctobe_id", flat=True)
        )
        if missref_label
        else set()
    )
    missref_intervals: dict[int, list] = {}
    for rfc in RfcToBe.objects.filter(pk__in=missref_ids):
        missref_intervals[rfc.pk] = [
            (iv.start, iv.end) for iv in rfc.time_intervals_with_label(missref_label)
        ]

    # Kept separate for the "entered with missing references" check, which grants
    # the not-received relation only an intake grace but the legacy MISSREF label
    # a week (see the *_ENTRY_GRACE constants).
    relation_merged: dict[int, list] = {}
    label_merged: dict[int, list] = {}
    for d in docs:
        enq = d["enqueued_at"]
        rel = notrecv.get(d["pk"], [])
        lab = missref_intervals.get(d["pk"], [])
        d["gone_to_edit"] = _first_clear_after(rel + lab, enq) if enq else None
        if rel:
            relation_merged[d["pk"]] = _merge_intervals(rel, now)
        if lab:
            label_merged[d["pk"]] = _merge_intervals(lab, now)

    # Historical page counts, only for docs entering / publishing / going to
    # edit in range.
    enq_pages: dict[int, int] = {}
    pub_pages: dict[int, int] = {}
    gone_pages: dict[int, int] = {}
    for d in docs:
        enq, pub, gte = d["enqueued_at"], d["published_at"], d["gone_to_edit"]
        if enq is not None and enq >= earliest:
            enq_pages[d["pk"]] = _pages_at(d["pk"], enq)
        if pub is not None and pub >= earliest:
            pub_pages[d["pk"]] = _pages_at(d["pk"], pub)
        if gte is not None and gte >= earliest:
            gone_pages[d["pk"]] = _pages_at(d["pk"], gte)

    # Full pages history per doc, to read the page count in effect at each
    # period boundary (for docs in the queue at the start of a period).
    pages_history: dict[int, list[tuple[datetime.datetime, int]]] = {}
    for hid, hdate, hpages in (
        RfcToBe.history.model.objects.filter(id__in=doc_ids)
        .order_by("id", "history_date")
        .values_list("id", "history_date", "pages")
    ):
        pages_history.setdefault(hid, []).append((hdate, hpages or 0))

    def pages_at_boundary(pk: int, when: datetime.datetime) -> int:
        val = 0
        for hdate, hpages in pages_history.get(pk, ()):
            if hdate <= when:
                val = hpages
            else:
                break
        return val

    # Blocked = the time view's blocked union, PLUS missing-reference coverage
    # (raw MISSREF + not-received relationships). Missing a reference is a blocked
    # condition, and unioning it bridges the legacy→relationship handoff at the
    # transition (where the blocked assignment is created a little after the
    # legacy state ends, leaving a spurious sub-day gap). Only docs that were ever
    # blocked or ever missing a reference need the walk; the rest are 0.
    legacy_ids = _legacy_state_doc_ids(doc_ids)
    relevant_ids = _blocked_doc_ids(doc_ids) | set(notrecv) | missref_ids
    blocked_intervals: dict[int, list] = {}
    for rfc in RfcToBe.objects.filter(pk__in=relevant_ids):
        base = document_intervals(rfc, now, include_legacy=rfc.pk in legacy_ids)[0]
        missing = notrecv.get(rfc.pk, []) + missref_intervals.get(rfc.pk, [])
        blocked_intervals[rfc.pk] = _merge_intervals(base + missing, now)

    periods: list[dict] = []
    for window in windows:
        start = window["start"]
        eff_end = min(window["end"], now)

        docs_at_start = docs_entered = docs_entered_missing_ref = pages_entered = 0
        pages_at_start = rfcs_published = pages_published = pages_to_edit = 0
        pages_blocked_end = pages_in_progress_end = 0
        docs_blocked_entire = rest = 0
        pct_sum = 0.0

        for d in docs:
            enq, pub = d["enqueued_at"], d["published_at"]
            if enq is None:
                continue
            if enq <= start and (pub is None or pub > start):
                docs_at_start += 1
                pages_at_start += pages_at_boundary(d["pk"], start)
            if start <= enq < eff_end:
                docs_entered += 1
                pages_entered += enq_pages.get(d["pk"], 0)
                if _missing_ref_at_entry(
                    relation_merged.get(d["pk"], []), enq, _MISSING_REF_ENTRY_GRACE
                ) or _missing_ref_at_entry(
                    label_merged.get(d["pk"], []), enq, _MISSREF_LABEL_ENTRY_GRACE
                ):
                    docs_entered_missing_ref += 1
            if pub is not None and start <= pub < eff_end:
                rfcs_published += 1
                pages_published += pub_pages.get(d["pk"], 0)
            gte = d["gone_to_edit"]
            if gte is not None and start <= gte < eff_end:
                pages_to_edit += gone_pages.get(d["pk"], 0)
            # State at the end of the period (as of "now" for the current one):
            # pages of docs still in the queue, split blocked vs in progress.
            if enq <= eff_end and (pub is None or pub > eff_end):
                end_pages = pages_at_boundary(d["pk"], eff_end)
                if _covered_at(blocked_intervals.get(d["pk"], []), eff_end):
                    pages_blocked_end += end_pages
                else:
                    pages_in_progress_end += end_pages
            # Member of the period: in the queue at some point within it.
            if enq <= eff_end and (pub is None or pub >= start):
                in_queue = (
                    min(pub or eff_end, eff_end) - max(enq, start)
                ).total_seconds()
                if in_queue <= 0:
                    continue
                blocked = _overlap_seconds(
                    blocked_intervals.get(d["pk"], []), start, eff_end
                )
                if blocked >= in_queue:  # blocked the whole time it was in queue
                    docs_blocked_entire += 1
                else:
                    rest += 1
                    pct_sum += min(blocked, in_queue) / in_queue

        periods.append(
            {
                "label": window["label"],
                "start": window["start"],
                "end": window["end"],
                "docs_at_start": docs_at_start,
                "docs_entered": docs_entered,
                "pages_at_start": pages_at_start,
                "pages_entered": pages_entered,
                "rfcs_published": rfcs_published,
                "pages_published": pages_published,
                "pages_to_edit": pages_to_edit,
                "pages_blocked_end": pages_blocked_end,
                "pages_in_progress_end": pages_in_progress_end,
                "docs_blocked_entire": docs_blocked_entire,
                "docs_entered_missing_ref": docs_entered_missing_ref,
                # Avg blocked share over the rest (not blocked the whole period)
                # and over all members (each blocked-entire doc counts as 100%).
                "avg_pct_blocked": round(pct_sum / rest * 100, 1) if rest else 0.0,
                "avg_pct_blocked_all": (
                    round((pct_sum + docs_blocked_entire) / members * 100, 1)
                    if (members := rest + docs_blocked_entire)
                    else 0.0
                ),
                "legacy_included": start < TRANSITION_DATE,
            }
        )
    return periods
