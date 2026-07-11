# Copyright The IETF Trust 2026, All Rights Reserved
"""Reconstruct a single document's time-in-assignment / time-blocked timeline.

All data is derived from django-simple-history records; nothing new is
persisted. Two eras are stitched together at ``TRANSITION_DATE``: on/after it,
"blocked" is an :class:`~rpc.models.Assignment` with ``role="blocked"`` and
"working" is any other active assignment; before it, old-system states were
captured as ``RfcToBe`` labels and are reconstructed via
:meth:`~rpc.models.RfcToBe.time_intervals_with_label`. Intervals straddling the
boundary are clipped at it so the two eras never double-count. Queue-wide
period aggregation lives in :mod:`rpc.lifecycle.rollups`.
"""

import datetime
from dataclasses import dataclass, field
from itertools import pairwise

from django.utils import timezone

from ..models import Assignment, Label, RfcToBe, RfcToBeBlockingReason
from .intervals import (
    Run,
    _active_runs,
    _clip,
    _merge_intervals,
    _split_runs_by_intervals,
    _subtract_intervals,
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
