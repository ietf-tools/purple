# Copyright The IETF Trust 2026, All Rights Reserved
"""Queue-wide period rollups for the statistics pages.

Aggregates per-document history into per-period (week / month / quarter / year /
IETF-meeting) figures for the Time, Counts and Stream tabs. The bulk ``*_by_doc``
helpers reload each document's history once, so a rollup runs a handful of
queries regardless of queue size. Per-document reconstruction and the shared
interval algebra live in :mod:`rpc.stats.timeline` and
:mod:`rpc.stats.intervals`.
"""

import datetime
from collections import namedtuple

from django.apps import apps
from django.db import models
from django.utils import timezone

from ..dt_v1_api_utils import datatracker_ietf_meetings
from ..models import (
    Assignment,
    DocRelationshipName,
    Label,
    RfcToBe,
    RfcToBeBlockingReason,
    RpcRelatedDocument,
)
from .intervals import (
    Run,
    active_runs,
    clip,
    covered_at,
    first_clear_after,
    intersect_intervals,
    merge_intervals,
    overlap_seconds,
    subtract_intervals,
)
from .timeline import (
    AWAITING_REF_LABEL_PREFIX,
    LEGACY_BLOCKED_LABEL_SLUGS,
    LEGACY_STATE_LABEL_SLUGS,
    TRANSITION_DATE,
)

# Lightweight stand-in for an assignment history record when read in bulk via
# ``.values_list`` — only the fields ``active_runs`` touches.
_HistRec = namedtuple("_HistRec", ["state", "history_date"])


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    """Return ``(year, month)`` shifted by ``delta`` months (month is 1-12)."""
    index = (year * 12 + (month - 1)) + delta
    return index // 12, index % 12 + 1


def _midnight_utc(d: datetime.date) -> datetime.datetime:
    """Return the aware datetime at 00:00 UTC on ``d``."""
    return datetime.datetime.combine(d, datetime.time.min, tzinfo=datetime.UTC)


def period_windows(period: str, count: int, now: datetime.datetime) -> list[dict]:
    """Windows, oldest first, ending with the current period.

    ``period`` is one of ``week`` / ``month`` / ``quarter`` / ``year`` (all
    calendar-aligned) or ``ietf`` (spans between consecutive IETF meetings).
    """
    if count < 1:
        return []
    # Take the calendar day in UTC so the window boundaries line up with
    # _midnight_utc(), which anchors each window's start/end at 00:00 UTC.
    today = now.astimezone(datetime.UTC).date()
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
        {"label": label, "start": _midnight_utc(start), "end": _midnight_utc(end)}
        for label, start, end in windows
    ]


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
    return covered_at(intervals, enq) or any(
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

    # Bulk-load every per-doc history walk the category build needs, so the
    # rollup runs a handful of queries instead of several per document.
    seg_by_doc = _assignment_segments_by_doc(doc_ids)
    legacy_slug_by_pk = (
        dict(
            Label.objects.filter(slug__in=LEGACY_STATE_LABEL_SLUGS).values_list(
                "pk", "slug"
            )
        )
        if include_legacy
        else {}
    )
    awaiting_pks = set(
        Label.objects.filter(slug__istartswith=AWAITING_REF_LABEL_PREFIX).values_list(
            "pk", flat=True
        )
    )
    label_iv = _label_intervals_by_doc(doc_ids, set(legacy_slug_by_pk) | awaiting_pks)
    reason_by_doc = _blocked_reason_intervals_by_doc(doc_ids, now)

    def _categories(doc_id: int) -> dict[str, tuple[bool, list]]:
        """Per-doc ``{category: (is_blocked, merged_intervals)}`` from bulk data.

        ``category`` is an assignment role slug (post-transition) or a legacy
        state label slug (pre-transition). ``awaiting ref:`` time is carved out of
        ``final_review_editor`` into a blocked ``awaiting_ref`` category, and — for
        docs with blocking reasons — the single ``blocked`` category is itemised
        into one blocked category per reason (mirroring the doc timeline). All
        sourced from the bulk lookups above rather than per-doc queries.
        """
        raw: dict[str, tuple[bool, list]] = {}
        for role_id, is_blocked, runs in seg_by_doc.get(doc_id, []):
            _b, intervals = raw.setdefault(role_id, (is_blocked, []))
            intervals.extend((start, end) for start, end, _state in runs)
        if doc_id in legacy_ids:
            for lpk, slug in legacy_slug_by_pk.items():
                is_blocked = slug in LEGACY_BLOCKED_LABEL_SLUGS
                for start, end in label_iv.get(doc_id, {}).get(lpk, []):
                    clipped = clip(start, end, hi=TRANSITION_DATE)
                    if clipped is None:
                        continue
                    _b, intervals = raw.setdefault(slug, (is_blocked, []))
                    intervals.append(clipped)
        result = {
            category: (is_blocked, merge_intervals(intervals, now))
            for category, (is_blocked, intervals) in raw.items()
        }
        if doc_id in awaiting_ids:
            awaiting_raw = [
                iv
                for lpk in awaiting_pks
                for iv in label_iv.get(doc_id, {}).get(lpk, [])
            ]
            awaiting = merge_intervals(awaiting_raw, now) if awaiting_raw else []
            if awaiting:
                fre = result.get("final_review_editor")
                if fre is not None:
                    result["final_review_editor"] = (
                        fre[0],
                        subtract_intervals(fre[1], awaiting),
                    )
                result["awaiting_ref"] = (True, awaiting)
        if doc_id in reason_ids:
            reasons = reason_by_doc.get(doc_id, {})
            if reasons:
                # Itemise the blocked category per reason. Constrain each reason
                # to the actual blocked-assignment time so a reason that overruns
                # it can't credit un-blocked time, and surface any blocked time no
                # reason explains as "blocked (other)", so the per-reason lanes
                # still sum to the blocked assignment.
                blocked_cat = result.pop("blocked", None)
                blocked_ivs = blocked_cat[1] if blocked_cat else []
                covered: list = []
                for name, intervals in reasons.items():
                    within = intersect_intervals(intervals, blocked_ivs)
                    if within:
                        result[name] = (True, within)
                        covered.extend(within)
                remainder = subtract_intervals(
                    blocked_ivs, merge_intervals(covered, now)
                )
                if remainder:
                    result["blocked (other)"] = (True, remainder)
        return result

    doc_data = [
        (rfc.enqueued_at, rfc.published_at, _categories(rfc.pk)) for rfc in docs
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
            # Bin membership: entered by the period end, and had not left the
            # queue before the period started. A doc with no enqueue time can't
            # be placed, so it is not a member (matching queue_counts_rollup).
            if enqueued is None or enqueued > eff_end:
                continue
            if published is not None and published < start:
                continue
            member_count += 1
            for role, (is_blocked, intervals) in categories.items():
                # Per-period flow: only the portion of each interval that falls
                # within this window, so long-running states (e.g. MISSREF, EDIT)
                # do not accumulate into an ever-growing cumulative total.
                seconds = overlap_seconds(intervals, start, eff_end)
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


def _missing_ref_intervals_by_doc(
    doc_ids: list[int],
) -> dict[int, list[tuple[datetime.datetime, datetime.datetime | None]]]:
    """Per-doc intervals during which a not-received reference existed.

    Reconstructed from :class:`~rpc.models.RpcRelatedDocument` history. A
    relationship row is a "missing reference" while it exists *and* carries a
    not-received (1g/2g/3g) slug. The reference can stop being missing two ways:
    the row is deleted (a ``-`` history row — 2g/3g refs), **or** the row's slug
    is upgraded in place (e.g. 1g ``not-received`` → ``refqueue`` when the draft
    arrives; a ``~`` row with a non-not-received slug and no delete). So we walk
    every history row of each relationship that was *ever* not-received and close
    the interval on whichever comes first, rather than only on a delete.
    """
    historical = RpcRelatedDocument.history.model
    not_received = set(DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUGS)
    ever_ids = set(
        historical.objects.filter(
            source_id__in=doc_ids, relationship__slug__in=not_received
        ).values_list("id", flat=True)
    )
    if not ever_ids:
        return {}

    # source -> relationship-row-id -> {"source", "open": start|None, "list": []}
    state: dict[int, dict] = {}
    rows = (
        historical.objects.filter(id__in=ever_ids)
        .order_by("history_date", "history_id")
        .values("id", "source_id", "history_type", "history_date", "relationship__slug")
    )
    for row in rows:
        st = state.setdefault(
            row["id"], {"source": row["source_id"], "open": None, "list": []}
        )
        # Missing while the row exists (not a delete) with a not-received slug.
        missing = (
            row["history_type"] != "-" and row["relationship__slug"] in not_received
        )
        if missing and st["open"] is None:
            st["open"] = row["history_date"]
        elif not missing and st["open"] is not None:
            st["list"].append((st["open"], row["history_date"]))
            st["open"] = None

    by_doc: dict[int, list] = {}
    for st in state.values():
        intervals = list(st["list"])
        if st["open"] is not None:
            intervals.append((st["open"], None))  # still missing → open
        if intervals:
            by_doc.setdefault(st["source"], []).extend(intervals)
    return by_doc


def _label_intervals_by_doc(
    doc_ids: list[int], label_pks: set[int]
) -> dict[int, dict[int, list[tuple[datetime.datetime, datetime.datetime | None]]]]:
    """Bulk equivalent of :meth:`RfcToBe.time_intervals_with_label` for many docs.

    Returns ``{doc_id: {label_pk: [(start, end|None), ...]}}`` restricted to
    ``label_pks``, reconstructed in two queries from the ``HistoricalRfcToBe``
    snapshots and their m2m label rows.

    Matches the per-doc method's semantics exactly: it walks the *label-set
    change-points* (snapshots whose full label set differs from the preceding
    one) and, at each one, opens a target label that is present-and-not-open and
    closes one that is open-and-now-absent. Change-points therefore depend on the
    whole label set (a change in any label can open a target label that was
    already present), which is why the full set is loaded, not just ``label_pks``.
    The earliest snapshot has no predecessor, so labels present only there are not
    counted — as in the per-doc method. Open spans are left ``None``.
    """
    if not doc_ids or not label_pks:
        return {}
    historical = RfcToBe.history.model
    snaps: dict[int, list[tuple[int, datetime.datetime]]] = {}
    for hid, hdate, oid in (
        historical.objects.filter(id__in=doc_ids)
        .order_by("id", "history_date", "history_id")
        .values_list("history_id", "history_date", "id")
    ):
        snaps.setdefault(oid, []).append((hid, hdate))

    through = apps.get_model("rpc", "HistoricalRfcToBeLabel")
    labels_at: dict[int, set[int]] = {}
    for m2m_history_id, label_id in through.objects.filter(
        rfctobe_id__in=doc_ids
    ).values_list("history_id", "label_id"):
        labels_at.setdefault(m2m_history_id, set()).add(label_id)

    out: dict[int, dict[int, list]] = {}
    for doc_id, seq in snaps.items():
        prev: set[int] | None = None
        open_start: dict[int, datetime.datetime] = {}
        per: dict[int, list] = {}
        for hid, hdate in seq:
            cur = labels_at.get(hid, set())
            if prev is None:
                prev = cur
                continue
            if cur != prev:  # a label-set change-point
                for lpk in label_pks:
                    if lpk in cur:
                        open_start.setdefault(lpk, hdate)
                    elif lpk in open_start:
                        per.setdefault(lpk, []).append((open_start.pop(lpk), hdate))
                prev = cur
        for lpk, start in open_start.items():
            per.setdefault(lpk, []).append((start, None))
        if per:
            out[doc_id] = per
    return out


def _assignment_segments_by_doc(
    doc_ids: list[int],
) -> dict[int, list[tuple[str, bool, list[Run]]]]:
    """Bulk :func:`_assignment_segments` — ``{doc_id: [(role, blocked, runs)]}``.

    Two queries (assignments + their history) instead of one-per-assignment.
    Runs are clipped to on/after the transition, exactly as the per-doc version.
    """
    if not doc_ids:
        return {}
    assignments = list(
        Assignment.objects.filter(rfc_to_be_id__in=doc_ids)
        .order_by("id")
        .values("id", "rfc_to_be_id", "role_id")
    )
    hist_by_assignment: dict[int, list] = {}
    for aid, state, hdate in (
        Assignment.history.model.objects.filter(rfc_to_be_id__in=doc_ids)
        .order_by("id", "history_date")
        .values_list("id", "state", "history_date")
    ):
        hist_by_assignment.setdefault(aid, []).append(_HistRec(state, hdate))

    out: dict[int, list] = {}
    for a in assignments:
        history = hist_by_assignment.get(a["id"])
        if not history:
            continue
        runs = []
        for start, end, state in active_runs(history):
            clipped = clip(start, end, lo=TRANSITION_DATE)
            if clipped is not None:
                runs.append((clipped[0], clipped[1], state))
        if runs:
            out.setdefault(a["rfc_to_be_id"], []).append(
                (a["role_id"], a["role_id"] == "blocked", runs)
            )
    return out


def _blocked_intervals_by_doc(
    doc_ids: list[int], now: datetime.datetime, legacy_ids: set[int]
) -> dict[int, list[tuple[datetime.datetime, datetime.datetime]]]:
    """Bulk equivalent of ``document_intervals(...)[0]`` — the blocked union.

    Blocked assignments (post-transition) + blocked-equivalent legacy labels
    (pre-transition, only for ``legacy_ids``) + any ``awaiting ref:`` time.
    """
    if not doc_ids:
        return {}
    seg = _assignment_segments_by_doc(doc_ids)
    legacy_blocked_pks = set(
        Label.objects.filter(slug__in=LEGACY_BLOCKED_LABEL_SLUGS).values_list(
            "pk", flat=True
        )
    )
    awaiting_pks = set(
        Label.objects.filter(slug__istartswith=AWAITING_REF_LABEL_PREFIX).values_list(
            "pk", flat=True
        )
    )
    label_iv = _label_intervals_by_doc(doc_ids, legacy_blocked_pks | awaiting_pks)
    out: dict[int, list] = {}
    for doc_id in doc_ids:
        raw: list = []
        for _role, is_blocked, runs in seg.get(doc_id, []):
            if is_blocked:
                raw.extend((start, end) for start, end, _state in runs)
        if doc_id in legacy_ids:
            for lpk in legacy_blocked_pks:
                for start, end in label_iv.get(doc_id, {}).get(lpk, []):
                    clipped = clip(start, end, hi=TRANSITION_DATE)
                    if clipped is not None:
                        raw.append(clipped)
        for lpk in awaiting_pks:  # awaiting time counts as blocked, all eras
            raw.extend(label_iv.get(doc_id, {}).get(lpk, []))
        out[doc_id] = merge_intervals(raw, now)
    return out


def _blocked_reason_intervals_by_doc(
    doc_ids: list[int], now: datetime.datetime
) -> dict[int, dict[str, list[tuple[datetime.datetime, datetime.datetime]]]]:
    """Per-doc merged blocked intervals keyed by blocking-reason name.

    Source for itemising the queue's blocked time by reason (same
    RfcToBeBlockingReason records as the doc timeline's reason lanes).
    Returns ``{doc_id: {reason_name: intervals}}``.
    """
    if not doc_ids:
        return {}
    raw: dict[int, dict[str, list]] = {}
    for doc_id, name, since, resolved in (
        RfcToBeBlockingReason.objects.filter(rfc_to_be_id__in=doc_ids)
        .order_by("since_when")
        .values_list("rfc_to_be_id", "reason__name", "since_when", "resolved")
    ):
        raw.setdefault(doc_id, {}).setdefault(name, []).append((since, resolved))
    return {
        doc_id: {name: merge_intervals(ivs, now) for name, ivs in by_reason.items()}
        for doc_id, by_reason in raw.items()
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
    missref_by_doc = (
        _label_intervals_by_doc(doc_ids, {missref_label.pk}) if missref_label else {}
    )
    missref_ids = set(missref_by_doc)
    missref_intervals: dict[int, list] = {
        pk: labels[missref_label.pk] for pk, labels in missref_by_doc.items()
    }

    # Kept separate for the "entered with missing references" check, which grants
    # the not-received relation only an intake grace but the legacy MISSREF label
    # a week (see the *_ENTRY_GRACE constants).
    relation_merged: dict[int, list] = {}
    label_merged: dict[int, list] = {}
    for d in docs:
        enq = d["enqueued_at"]
        rel = notrecv.get(d["pk"], [])
        lab = missref_intervals.get(d["pk"], [])
        d["gone_to_edit"] = first_clear_after(rel + lab, enq) if enq else None
        if rel:
            relation_merged[d["pk"]] = merge_intervals(rel, now)
        if lab:
            label_merged[d["pk"]] = merge_intervals(lab, now)

    # Full pages history per doc (one query), to read the page count in effect
    # at any instant — period boundaries, enqueue, publish, gone-to-edit.
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

    # Page counts for docs entering / publishing / going to edit in range,
    # read from that in-memory history (no per-doc query).
    enq_pages: dict[int, int] = {}
    pub_pages: dict[int, int] = {}
    gone_pages: dict[int, int] = {}
    for d in docs:
        enq, pub, gte = d["enqueued_at"], d["published_at"], d["gone_to_edit"]
        if enq is not None and enq >= earliest:
            enq_pages[d["pk"]] = pages_at_boundary(d["pk"], enq)
        if pub is not None and pub >= earliest:
            pub_pages[d["pk"]] = pages_at_boundary(d["pk"], pub)
        if gte is not None and gte >= earliest:
            gone_pages[d["pk"]] = pages_at_boundary(d["pk"], gte)

    # Blocked = the time view's blocked union, PLUS missing-reference coverage
    # (raw MISSREF + not-received relationships). Missing a reference is a blocked
    # condition, and unioning it bridges the legacy→relationship handoff at the
    # transition (where the blocked assignment is created a little after the
    # legacy state ends, leaving a spurious sub-day gap). Only docs that were ever
    # blocked or ever missing a reference need the walk; the rest are 0.
    legacy_ids = _legacy_state_doc_ids(doc_ids)
    relevant_ids = _blocked_doc_ids(doc_ids) | set(notrecv) | missref_ids
    base_blocked = _blocked_intervals_by_doc(list(relevant_ids), now, legacy_ids)
    blocked_intervals: dict[int, list] = {}
    for pk in relevant_ids:
        missing = notrecv.get(pk, []) + missref_intervals.get(pk, [])
        blocked_intervals[pk] = merge_intervals(base_blocked.get(pk, []) + missing, now)

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
                if covered_at(blocked_intervals.get(d["pk"], []), eff_end):
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
                blocked = overlap_seconds(
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


# Stream keys shown on the "Stream" stats tab, in display order (legacy is
# dropped). The IETF stream is always split into WG vs AD-sponsored (a doc with
# no originating group is AD-sponsored); the frontend can merge them back into a
# single "IETF" via its toggle.
PUBLISHED_STREAM_LABELS = {
    "ietf-wg": "IETF WG",
    "ietf-ad": "IETF AD-sponsored",
    "ise": "ISE",
    "irtf": "IRTF",
    "iab": "IAB",
    "editorial": "Editorial",
}
# The stream keys, as serializer choices (see PUBLISHED_STATUS_ORDER's use).
PUBLISHED_STREAMS = tuple(PUBLISHED_STREAM_LABELS)

# Publication std-level slug -> status bucket, and the bucket display order.
_STD_LEVEL_BUCKET = {
    "ps": "Standards Track",
    "std": "Standards Track",
    "ds": "Standards Track",
    "bcp": "Best Current Practice",
    "exp": "Experimental",
    "inf": "Informational",
    "hist": "Historic",
    "unkn": "Unknown",
}

PUBLISHED_STATUS_ORDER = [
    "Standards Track",
    "Best Current Practice",
    "Experimental",
    "Informational",
    "Historic",
    "Unknown",
]


def queue_published_rollup(
    period: str, count: int, now: datetime.datetime | None = None
) -> dict:
    """Per-period counts of RFCs published, grouped by stream and status.

    "Stream" and "status" are the values *at publication* (``publication_stream``
    / ``publication_std_level``, falling back to the current fields when blank).
    Std levels fold into named buckets (Standards Track = ps/std/ds, etc.); any
    other slug is "Unknown". Only the IETF/ISE/IRTF/IAB/Editorial streams are
    counted, and the IETF stream is split into ``ietf-wg`` / ``ietf-ad`` (no
    originating group = AD-sponsored). The returned ``streams`` and ``statuses``
    are the ones with a non-zero count in at least one period (so all-zero
    rows/segments drop out), in display order; ``periods[i].counts`` lists only
    the non-zero cells.
    """
    now = now or timezone.now()
    windows = period_windows(period, count, now)
    if not windows:
        return {"streams": [], "statuses": [], "periods": []}
    earliest = windows[0]["start"]

    docs = RfcToBe.objects.filter(published_at__gte=earliest).values_list(
        "published_at",
        "publication_stream_id",
        "stream_id",
        "publication_std_level_id",
        "std_level_id",
        "group",
    )
    # per-period {(stream, status): count}
    per_counts: list[dict[tuple[str, str], int]] = [{} for _ in windows]
    bounds = [(w["start"], min(w["end"], now)) for w in windows]
    for pub, pub_stream, stream, pub_level, level, group in docs:
        stream = pub_stream or stream
        if stream == "ietf":
            stream = "ietf-wg" if (group or "").strip() else "ietf-ad"
        if stream not in PUBLISHED_STREAM_LABELS:
            continue
        status = _STD_LEVEL_BUCKET.get(pub_level or level, "Unknown")
        for i, (start, end) in enumerate(bounds):
            if start <= pub < end:
                key = (stream, status)
                per_counts[i][key] = per_counts[i].get(key, 0) + 1
                break

    seen: set = set().union(*per_counts) if per_counts else set()
    streams = [s for s in PUBLISHED_STREAM_LABELS if any(s == k[0] for k in seen)]
    statuses = [s for s in PUBLISHED_STATUS_ORDER if any(s == k[1] for k in seen)]

    periods = [
        {
            "label": w["label"],
            "start": w["start"],
            "end": w["end"],
            "counts": [
                {"stream": st, "status": status, "count": n}
                for (st, status), n in counts.items()
            ],
        }
        for w, counts in zip(windows, per_counts, strict=True)
    ]
    return {"streams": streams, "statuses": statuses, "periods": periods}
