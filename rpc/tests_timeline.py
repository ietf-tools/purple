# Copyright The IETF Trust 2026, All Rights Reserved
"""Tests for rpc.lifecycle.timeline and the timeline/queue-stats endpoints."""

import datetime
import time
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .factories import (
    AssignmentFactory,
    DispositionNameFactory,
    LabelFactory,
    RfcToBeFactory,
    RpcRoleFactory,
)
from .lifecycle import timeline
from .lifecycle.timeline import (
    KIND_AWAITING,
    KIND_BLOCKED,
    KIND_LEGACY,
    KIND_WORKING,
    TRANSITION_DATE,
    _active_runs,
    _candidate_docs,
    _clip,
    _first_clear_after,
    _merge_intervals,
    _missing_ref_intervals_by_doc,
    _overlap_seconds,
    assignment_tracks,
    blocked_reason_bands,
    build_document_timeline,
    document_intervals,
    period_windows,
    queue_counts_rollup,
    queue_rollup,
)
from .models import (
    BlockingReason,
    DocRelationshipName,
    RfcToBeBlockingReason,
    RpcRelatedDocument,
)

UTC = datetime.UTC
DAY = datetime.timedelta(days=1)


def _dt(year, month, day):
    return datetime.datetime(year, month, day, tzinfo=UTC)


def _make_assignment(rfc, role_slug, transitions, person=None):
    """Create an Assignment and rewrite its history to the given transitions.

    ``transitions`` is a list of ``(datetime, state)`` in chronological order;
    the first is the creation state.
    """
    role = RpcRoleFactory(slug=role_slug)
    # person defaults to None to avoid datatracker plain_name lookups in tests.
    assignment = AssignmentFactory(
        rfc_to_be=rfc, role=role, state=transitions[0][1], person=person
    )
    for _when, state in transitions[1:]:
        assignment.state = state
        assignment.save()
    records = list(assignment.history.all().order_by("history_id"))
    assert len(records) == len(transitions), (len(records), len(transitions))
    for record, (when, _state) in zip(records, transitions, strict=True):
        record.history_date = when
        record.save()
    return assignment


def _backdate_creation(rfc, when):
    """Set the doc's creation (enqueue) history date, which drives bin
    membership in the queue rollup."""
    create_rec = rfc.history.filter(history_type="+").order_by("history_date").first()
    create_rec.history_date = when
    create_rec.save()


def _missing_ref_over(rfc, start, end):
    """Give ``rfc`` a not-received reference active over ``[start, end)``."""
    rel, _ = DocRelationshipName.objects.get_or_create(
        slug="not-received", defaults={"name": "Not Received", "desc": ""}
    )
    rrd = RpcRelatedDocument.objects.create(
        relationship=rel, source=rfc, target_rfctobe=RfcToBeFactory()
    )
    hist = RpcRelatedDocument.history
    add = hist.filter(id=rrd.pk, history_type="+").first()
    add.history_date = start
    add.save()
    rid = rrd.pk
    rrd.delete()
    rm = hist.filter(id=rid, history_type="-").order_by("-history_id").first()
    rm.history_date = end
    rm.save()


def _missing_ref_upgraded(rfc, start, upgraded):
    """not-received reference added at ``start``, upgraded to refqueue at
    ``upgraded`` in place (the 1g-resolution path — no delete row)."""
    nr, _ = DocRelationshipName.objects.get_or_create(
        slug="not-received", defaults={"name": "Not Received", "desc": ""}
    )
    refqueue, _ = DocRelationshipName.objects.get_or_create(
        slug="refqueue", defaults={"name": "Ref Queue", "desc": ""}
    )
    rrd = RpcRelatedDocument.objects.create(
        relationship=nr, source=rfc, target_rfctobe=RfcToBeFactory()
    )
    hist = RpcRelatedDocument.history
    add = hist.filter(id=rrd.pk, history_type="+").first()
    add.history_date = start
    add.save()
    rrd.relationship = refqueue  # resolve in place, as rpc.api does for 1g refs
    rrd.save()
    upd = hist.filter(id=rrd.pk, history_type="~").order_by("-history_id").first()
    upd.history_date = upgraded
    upd.save()


def _apply_label_over(rfc, label, start, end):
    """Give ``rfc`` ``label`` for the interval ``[start, end)`` via history."""
    # The document is created before any label is applied, so backdate the
    # creation record (as is always the case in production).
    create_rec = rfc.history.filter(history_type="+").first()
    if create_rec and create_rec.history_date >= start:
        create_rec.history_date = start - DAY
        create_rec.save()
    rfc.labels.add(label)
    add_rec = rfc.history.order_by("-history_id").first()
    add_rec.history_date = start
    add_rec.save()
    rfc.labels.remove(label)
    rm_rec = rfc.history.order_by("-history_id").first()
    rm_rec.history_date = end
    rm_rec.save()


class PureHelperTests(SimpleTestCase):
    def test_clip_within_bounds(self):
        assert _clip(_dt(2026, 6, 1), _dt(2026, 6, 10)) == (
            _dt(2026, 6, 1),
            _dt(2026, 6, 10),
        )

    def test_clip_lo_trims_start(self):
        assert _clip(_dt(2026, 5, 1), _dt(2026, 6, 1), lo=_dt(2026, 5, 20)) == (
            _dt(2026, 5, 20),
            _dt(2026, 6, 1),
        )

    def test_clip_hi_trims_open_end(self):
        assert _clip(_dt(2026, 5, 1), None, hi=_dt(2026, 5, 20)) == (
            _dt(2026, 5, 1),
            _dt(2026, 5, 20),
        )

    def test_clip_empty_returns_none(self):
        assert _clip(_dt(2026, 6, 1), _dt(2026, 7, 1), lo=_dt(2026, 7, 1)) is None

    def test_merge_overlapping_and_open(self):
        now = _dt(2026, 6, 30)
        merged = _merge_intervals(
            [
                (_dt(2026, 6, 1), _dt(2026, 6, 10)),
                (_dt(2026, 6, 5), _dt(2026, 6, 12)),
                (_dt(2026, 6, 20), None),
            ],
            now,
        )
        assert merged == [
            (_dt(2026, 6, 1), _dt(2026, 6, 12)),
            (_dt(2026, 6, 20), now),
        ]

    def test_overlap_seconds_clips_to_window(self):
        seconds = _overlap_seconds(
            [(_dt(2026, 6, 1), _dt(2026, 6, 11))],
            _dt(2026, 6, 5),
            _dt(2026, 7, 1),
        )
        assert seconds == 6 * 24 * 3600

    def test_first_clear_after(self):
        d1, d2, d3 = _dt(2026, 1, 1), _dt(2026, 2, 1), _dt(2026, 3, 1)
        d4 = _dt(2026, 4, 1)
        assert _first_clear_after([], d2) == d2  # never missing -> clear at enqueue
        assert _first_clear_after([(d1, d3)], d2) == d3  # inside -> clears at end
        assert _first_clear_after([(d1, None)], d2) is None  # ongoing -> never clears
        assert _first_clear_after([(d3, d4)], d2) == d2  # missing starts later
        assert _first_clear_after([(d1, d2), (d3, d4)], d2) == d2  # clear in the gap

    def test_active_runs_split_by_inactive(self):
        class Rec:
            def __init__(self, state, when):
                self.state = state
                self.history_date = when

        runs = _active_runs(
            [
                Rec("assigned", _dt(2026, 6, 1)),
                Rec("closed_for_hold", _dt(2026, 6, 5)),
                Rec("in_progress", _dt(2026, 6, 8)),
                Rec("done", _dt(2026, 6, 11)),
            ]
        )
        assert runs == [
            (_dt(2026, 6, 1), _dt(2026, 6, 5), "assigned"),
            (_dt(2026, 6, 8), _dt(2026, 6, 11), "in_progress"),
        ]

    def test_active_runs_open_ended(self):
        class Rec:
            def __init__(self, state, when):
                self.state = state
                self.history_date = when

        runs = _active_runs([Rec("in_progress", _dt(2026, 6, 1))])
        assert runs == [(_dt(2026, 6, 1), None, "in_progress")]


class PeriodWindowTests(SimpleTestCase):
    def test_month_windows_oldest_first(self):
        windows = period_windows("month", 3, _dt(2026, 7, 15))
        assert [w["label"] for w in windows] == ["2026-05", "2026-06", "2026-07"]
        assert windows[0]["start"] == _dt(2026, 5, 1)
        assert windows[-1]["end"] == _dt(2026, 8, 1)

    def test_quarter_windows(self):
        windows = period_windows("quarter", 2, _dt(2026, 5, 10))
        assert [w["label"] for w in windows] == ["2026 Q1", "2026 Q2"]
        assert windows[0]["start"] == _dt(2026, 1, 1)
        assert windows[1]["end"] == _dt(2026, 7, 1)

    def test_year_windows(self):
        windows = period_windows("year", 2, _dt(2026, 5, 10))
        assert [w["label"] for w in windows] == ["2025", "2026"]
        assert windows[0]["start"] == _dt(2025, 1, 1)
        assert windows[1]["end"] == _dt(2027, 1, 1)

    def test_week_windows_align_to_monday(self):
        # 2026-07-15 is a Wednesday; its ISO week starts Monday 2026-07-13.
        windows = period_windows("week", 2, _dt(2026, 7, 15))
        assert windows[-1]["start"] == _dt(2026, 7, 13)
        assert windows[-1]["end"] == _dt(2026, 7, 20)

    # IETF meetings, date ascending; two of these are in the future relative to
    # the 2026-07-10 "now" used below (IETF 126 on 07-18 and IETF 127 in Nov).
    IETF_MEETINGS = [
        ("122", datetime.date(2025, 3, 15)),
        ("123", datetime.date(2025, 7, 19)),
        ("124", datetime.date(2025, 11, 1)),
        ("125", datetime.date(2026, 3, 14)),
        ("126", datetime.date(2026, 7, 18)),
        ("127", datetime.date(2026, 11, 14)),
    ]

    def test_ietf_windows_end_at_nearest_future_meeting(self):
        with mock.patch.object(
            timeline, "datatracker_ietf_meetings", return_value=self.IETF_MEETINGS
        ):
            windows = period_windows("ietf", 3, _dt(2026, 7, 10))
        # Current period ends at IETF 126 (nearest future), IETF 127 excluded.
        assert [w["label"] for w in windows] == ["IETF 124", "IETF 125", "IETF 126"]
        assert windows[-1]["start"] == _dt(2026, 3, 14)
        assert windows[-1]["end"] == _dt(2026, 7, 18)

    def test_ietf_windows_no_future_meeting(self):
        with mock.patch.object(
            timeline, "datatracker_ietf_meetings", return_value=self.IETF_MEETINGS
        ):
            windows = period_windows("ietf", 2, _dt(2027, 1, 1))
        # No future meeting: current period ends at the most recent past one.
        assert [w["label"] for w in windows] == ["IETF 126", "IETF 127"]
        assert windows[-1]["end"] == _dt(2026, 11, 14)

    def test_ietf_windows_too_few_meetings(self):
        one_meeting = [("127", datetime.date(2026, 11, 14))]
        with mock.patch.object(
            timeline, "datatracker_ietf_meetings", return_value=one_meeting
        ):
            assert period_windows("ietf", 3, _dt(2026, 7, 10)) == []

    def test_zero_count_is_empty(self):
        assert period_windows("month", 0, _dt(2026, 7, 15)) == []

    def test_unknown_period_raises(self):
        with self.assertRaises(ValueError):
            period_windows("decade", 1, _dt(2026, 7, 15))


class AssignmentTimelineTests(TestCase):
    def setUp(self):
        self.now = _dt(2026, 7, 1)

    def test_working_and_blocked_tracks(self):
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 11), "done")],
        )
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        tracks = timeline.assignment_tracks(rfc)
        by_role = {t.role: t for t in tracks}
        assert set(by_role) == {"first_editor", "blocked"}
        assert by_role["blocked"].is_blocked is True
        assert by_role["first_editor"].is_blocked is False
        seg = by_role["first_editor"].segments[0]
        assert seg.kind == KIND_WORKING
        assert seg.start == _dt(2026, 6, 1)
        assert seg.end == _dt(2026, 6, 11)

    def test_document_intervals_split_blocked_working(self):
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 11), "done")],
        )
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        blocked, working = document_intervals(rfc, self.now)
        assert working == [(_dt(2026, 6, 1), _dt(2026, 6, 11))]
        assert blocked == [(_dt(2026, 6, 15), _dt(2026, 6, 18))]

    def test_assignment_before_transition_is_clipped(self):
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 5, 10), "assigned"), (_dt(2026, 5, 25), "done")],
        )
        _blocked, working = document_intervals(rfc, self.now)
        # Span started before the transition; the pre-transition part is dropped.
        assert working == [(TRANSITION_DATE, _dt(2026, 5, 25))]

    def test_legacy_state_labels_before_transition(self):
        rfc = RfcToBeFactory()
        # IANA is a recognized blocking legacy state; EDIT is active work.
        blocking_state = LabelFactory(slug="IANA")
        working_state = LabelFactory(slug="EDIT")
        # A complexity/type label that must be ignored (not a workflow state).
        noise = LabelFactory(slug="refs: hard")
        _apply_label_over(rfc, blocking_state, _dt(2026, 3, 1), _dt(2026, 3, 15))
        _apply_label_over(rfc, working_state, _dt(2026, 4, 1), _dt(2026, 4, 8))
        _apply_label_over(rfc, noise, _dt(2026, 4, 10), _dt(2026, 4, 20))

        bands = {b.label: b for b in timeline.legacy_bands(rfc)}
        assert set(bands) == {"IANA", "EDIT"}  # "refs: hard" ignored
        assert bands["IANA"].kind == KIND_BLOCKED
        assert bands["EDIT"].kind == KIND_LEGACY

        blocked, working = document_intervals(rfc, self.now)
        assert (_dt(2026, 3, 1), _dt(2026, 3, 15)) in blocked
        assert (_dt(2026, 4, 1), _dt(2026, 4, 8)) in working

    def test_include_legacy_false_skips_labels(self):
        rfc = RfcToBeFactory()
        _apply_label_over(
            rfc, LabelFactory(slug="IANA"), _dt(2026, 3, 1), _dt(2026, 3, 15)
        )
        blocked, working = document_intervals(rfc, self.now, include_legacy=False)
        assert blocked == []
        assert working == []

    def test_build_document_timeline_shape(self):
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 11), "done")],
        )
        # A blocked assignment is itemised per reason, not shown as a track.
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        payload = build_document_timeline(rfc, self.now)
        assert payload["transition_date"] == TRANSITION_DATE
        assert {b.kind for b in payload["summary"]} == {KIND_BLOCKED, KIND_WORKING}
        assert "blocked_reasons" in payload
        # Only the non-blocked assignment remains a track.
        assert [t.role for t in payload["tracks"]] == ["first_editor"]

    def test_blocked_reason_bands(self):
        rfc = RfcToBeFactory()
        author, _ = BlockingReason.objects.get_or_create(
            slug="label_author_input_required",
            defaults={"name": "Author Input Required"},
        )
        actionholder, _ = BlockingReason.objects.get_or_create(
            slug="actionholder_active",
            defaults={"name": "Waiting for Action Holder"},
        )
        # Author-input applied twice (two stints); action-holder still open.
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason=author,
            since_when=_dt(2026, 6, 1), resolved=_dt(2026, 6, 5),
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason=author,
            since_when=_dt(2026, 6, 20), resolved=_dt(2026, 6, 22),
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason=actionholder,
            since_when=_dt(2026, 6, 25), resolved=None,
        )
        bands = blocked_reason_bands(rfc, self.now)
        assert {b.label for b in bands} == {author.name, actionholder.name}
        assert all(b.kind == KIND_BLOCKED for b in bands)
        by_label = {b.label: b for b in bands}
        # Two stints -> two segments; unresolved reason stays open-ended.
        assert len(by_label[author.name].segments) == 2
        actionholder_seg = by_label[actionholder.name].segments[0]
        assert actionholder_seg.end is None

    def test_final_review_editor_split_by_awaiting_ref(self):
        now = _dt(2026, 9, 1)
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "final_review_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 8, 1), "done")],
        )
        # "awaiting ref:" label applied for part of the final-review window.
        _apply_label_over(
            rfc,
            LabelFactory(slug="awaiting ref: RFC-to-be 1234"),
            _dt(2026, 6, 10),
            _dt(2026, 6, 20),
        )
        tracks = assignment_tracks(rfc, now)
        fre = [t for t in tracks if t.role == "final_review_editor"]
        kinds = {t.segments[0].kind for t in fre}
        assert kinds == {KIND_WORKING, KIND_AWAITING}
        awaiting = next(t for t in fre if t.segments[0].kind == KIND_AWAITING)
        working = next(t for t in fre if t.segments[0].kind == KIND_WORKING)
        # Awaiting = the labelled sub-interval (10 days), counted as blocked.
        assert len(awaiting.segments) == 1
        assert awaiting.segments[0].start == _dt(2026, 6, 10)
        assert awaiting.segments[0].end == _dt(2026, 6, 20)
        assert awaiting.is_blocked is True
        # Working = the surrounding time, in two pieces, not blocked.
        assert len(working.segments) == 2
        assert working.is_blocked is False

        # The awaiting-ref window counts as blocked in the doc summary, and is
        # carved out of working time.
        blocked, work = document_intervals(rfc, now)
        assert (_dt(2026, 6, 10), _dt(2026, 6, 20)) in blocked
        assert (_dt(2026, 6, 1), _dt(2026, 6, 10)) in work
        assert (_dt(2026, 6, 20), _dt(2026, 8, 1)) in work


class QueueRollupTests(TestCase):
    def setUp(self):
        self.now = _dt(2026, 7, 1)

    def _doc_with_work(self, disposition_slug="in_progress", published_at=None):
        rfc = RfcToBeFactory(
            disposition=DispositionNameFactory(slug=disposition_slug),
            published_at=published_at,
        )
        _backdate_creation(rfc, _dt(2026, 1, 1))
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 11), "done")],
        )
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        return rfc

    def test_per_role_breakdown_and_totals(self):
        self._doc_with_work()
        june = queue_rollup("month", 2, self.now)[0]
        assert june["label"] == "2026-06"
        assert june["doc_count"] == 1
        # Time spent within the period, broken out per role.
        assert june["total_working_seconds"] == 10 * 24 * 3600
        assert june["total_blocked_seconds"] == 3 * 24 * 3600
        by_role = {r["role"]: r for r in june["by_role"]}
        assert by_role["first_editor"]["is_blocked"] is False
        assert by_role["first_editor"]["seconds"] == 10 * 24 * 3600
        assert by_role["blocked"]["is_blocked"] is True
        assert by_role["blocked"]["seconds"] == 3 * 24 * 3600
        assert june["legacy_included"] is False

    def test_time_is_per_period_not_cumulative(self):
        # A single long-running interval spanning two months must be split
        # across the bins (per-period flow), not counted in full in each. Uses
        # fully post-transition dates so the TRANSITION_DATE clip doesn't apply.
        now = _dt(2026, 9, 1)
        rfc = RfcToBeFactory(disposition=DispositionNameFactory(slug="in_progress"))
        _backdate_creation(rfc, _dt(2026, 1, 1))
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 8, 1), "done")],
        )
        periods = {p["label"]: p for p in queue_rollup("month", 4, now)}
        # June [06-01, 07-01] = 30 days; July [07-01, 08-01] = 31 days; the
        # interval ends 08-01 so August contributes nothing.
        assert periods["2026-06"]["total_working_seconds"] == 30 * 24 * 3600
        assert periods["2026-07"]["total_working_seconds"] == 31 * 24 * 3600
        assert periods["2026-08"]["total_working_seconds"] == 0

    def test_awaiting_ref_counts_as_blocked_in_stats(self):
        rfc = RfcToBeFactory()
        _backdate_creation(rfc, _dt(2026, 1, 1))
        _make_assignment(
            rfc,
            "final_review_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 30), "done")],
        )
        _apply_label_over(
            rfc,
            LabelFactory(slug="awaiting ref: RFC-to-be 1234"),
            _dt(2026, 6, 10),
            _dt(2026, 6, 20),
        )
        june = queue_rollup("month", 2, self.now)[0]
        assert june["label"] == "2026-06"
        by_role = {r["role"]: r for r in june["by_role"]}
        # 10 days of awaiting-ref time counts as blocked under its own category.
        assert by_role["awaiting_ref"]["is_blocked"] is True
        assert by_role["awaiting_ref"]["seconds"] == 10 * 24 * 3600
        # ...and is carved out of the final_review_editor (working) time.
        assert by_role["final_review_editor"]["is_blocked"] is False
        assert by_role["final_review_editor"]["seconds"] == 19 * 24 * 3600
        assert june["total_blocked_seconds"] == 10 * 24 * 3600
        assert june["total_working_seconds"] == 19 * 24 * 3600

    def test_blocked_time_itemised_by_reason_in_stats(self):
        rfc = RfcToBeFactory()
        _backdate_creation(rfc, _dt(2026, 1, 1))
        # A blocked assignment whose time is itemised by reason below.
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 1), "in_progress"), (_dt(2026, 6, 30), "done")],
        )
        author, _ = BlockingReason.objects.get_or_create(
            slug="label_author_input_required",
            defaults={"name": "Author Input Required"},
        )
        holder, _ = BlockingReason.objects.get_or_create(
            slug="actionholder_active",
            defaults={"name": "Waiting for Action Holder"},
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason=author,
            since_when=_dt(2026, 6, 5), resolved=_dt(2026, 6, 15),
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc, reason=holder,
            since_when=_dt(2026, 6, 20), resolved=_dt(2026, 6, 25),
        )
        june = queue_rollup("month", 2, self.now)[0]
        by_role = {r["role"]: r for r in june["by_role"]}
        # The single "blocked" category is replaced by per-reason categories.
        assert "blocked" not in by_role
        assert by_role[author.name]["is_blocked"] is True
        assert by_role[author.name]["seconds"] == 10 * 24 * 3600
        assert by_role[holder.name]["seconds"] == 5 * 24 * 3600
        assert june["total_blocked_seconds"] == 15 * 24 * 3600

    def test_withdrawn_docs_excluded(self):
        self._doc_with_work(disposition_slug="withdrawn")
        periods = queue_rollup("month", 2, self.now)
        assert periods[0]["doc_count"] == 0
        assert periods[0]["total_working_seconds"] == 0

    def test_published_in_range_included(self):
        self._doc_with_work(disposition_slug="published", published_at=_dt(2026, 6, 20))
        june = queue_rollup("month", 2, self.now)[0]
        assert june["doc_count"] == 1
        assert june["total_working_seconds"] == 10 * 24 * 3600

    def test_membership_snapshot_by_period_end(self):
        # A doc created after a period's end is not a member of that period.
        rfc = RfcToBeFactory()
        _backdate_creation(rfc, _dt(2026, 6, 15))  # created mid-June
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 16), "assigned"), (_dt(2026, 6, 20), "done")],
        )
        # month x3 ending 2026-07-01 -> May, June, July windows.
        periods = {p["label"]: p for p in queue_rollup("month", 3, self.now)}
        # Not created until mid-June, so absent from the May bin (ends June 1).
        assert periods["2026-05"]["doc_count"] == 0
        assert periods["2026-06"]["doc_count"] == 1

    def test_legacy_included_flag_for_old_period(self):
        periods = queue_rollup("month", 6, _dt(2026, 7, 1))
        by_label = {p["label"]: p for p in periods}
        assert by_label["2026-03"]["legacy_included"] is True
        assert by_label["2026-06"]["legacy_included"] is False

    def test_legacy_only_doc_contributes_to_old_period(self):
        # No assignment, just a pre-transition state label. It must still be
        # picked up as a candidate and contribute to the March window.
        rfc = RfcToBeFactory()
        _apply_label_over(
            rfc, LabelFactory(slug="IANA"), _dt(2026, 3, 1), _dt(2026, 3, 15)
        )
        periods = queue_rollup("month", 6, self.now)
        by_label = {p["label"]: p for p in periods}
        assert by_label["2026-03"]["total_blocked_seconds"] == 14 * 24 * 3600

    def test_candidate_docs_filtering(self):
        earliest = _dt(2026, 6, 1)
        # Included: has an assignment.
        with_assignment = self._doc_with_work()
        # Included: legacy state label, published within range.
        legacy_only = RfcToBeFactory(
            disposition=DispositionNameFactory(slug="published"),
            published_at=_dt(2026, 6, 10),
        )
        _apply_label_over(
            legacy_only, LabelFactory(slug="TI"), _dt(2026, 3, 1), _dt(2026, 3, 5)
        )
        # Excluded: published before the range.
        old_published = self._doc_with_work(disposition_slug="published")
        old_published.published_at = _dt(2026, 1, 1)
        old_published.save()
        # Excluded: no assignment, only a non-state (complexity) label.
        RfcToBeFactory().labels.add(LabelFactory(slug="refs: hard"))

        ids = set(
            _candidate_docs(earliest, include_legacy=True).values_list("pk", flat=True)
        )
        assert with_assignment.pk in ids
        assert legacy_only.pk in ids
        assert old_published.pk not in ids


class QueueCountsRollupTests(TestCase):
    def setUp(self):
        self.now = _dt(2026, 7, 1)  # June window = [06-01, 07-01)

    def _doc(self, enq, *, pages=0, published_at=None, slug="in_progress"):
        rfc = RfcToBeFactory(
            disposition=DispositionNameFactory(slug=slug),
            published_at=published_at,
            pages=pages,
        )
        _backdate_creation(rfc, enq)
        return rfc

    def test_counts_rollup(self):
        # A: in queue since May, missing a reference until June 10 -> goes to
        # edit June 10 (10 pages). not-received is not "blocked" time.
        a = self._doc(_dt(2026, 5, 1), pages=10)
        _missing_ref_over(a, _dt(2026, 5, 1), _dt(2026, 6, 10))
        # B: enters in June with no missing refs -> goes to edit at entry.
        self._doc(_dt(2026, 6, 5), pages=20)
        # C: in queue since January, published in June (no missing refs).
        self._doc(
            _dt(2026, 1, 1), pages=5, published_at=_dt(2026, 6, 20), slug="published"
        )
        # D: in queue since May, blocked the entire month (went to edit at entry).
        d = self._doc(_dt(2026, 5, 1), pages=8)
        _make_assignment(
            d, "blocked",
            [(_dt(2026, 5, 25), "in_progress"), (_dt(2026, 7, 5), "done")],
        )

        june = queue_counts_rollup("month", 2, self.now)[0]
        assert june["label"] == "2026-06"
        assert june["docs_at_start"] == 3  # A, C, D (B enters mid-month)
        assert june["docs_entered"] == 1  # B
        assert june["docs_entered_missing_ref"] == 0  # B enters with no missing refs
        assert june["pages_at_start"] == 23  # A(10) + C(5) + D(8)
        assert june["pages_entered"] == 20
        assert june["rfcs_published"] == 1  # C
        assert june["pages_published"] == 5  # C
        # A clears its missing ref in June (10); B enters clear in June (20).
        assert june["pages_to_edit"] == 30
        # At end of June (self.now): A(10) went to edit, so workable/in progress;
        # B(20) in progress; C(5) published (gone); D(8) still blocked.
        assert june["pages_blocked_end"] == 8  # D
        assert june["pages_in_progress_end"] == 30  # A(10) + B(20)
        assert june["docs_blocked_entire"] == 1  # D
        # Rest = A, B, C. A is blocked (missing ref) 9 of 30 June days = 30%.
        assert june["avg_pct_blocked"] == 10.0  # (30 + 0 + 0) / 3
        # All 4 members: D 100%, A 30%, B/C 0% -> mean 32.5%.
        assert june["avg_pct_blocked_all"] == 32.5

    def test_docs_entering_with_missing_references(self):
        # E enters in June already missing a reference; F enters clean.
        e = self._doc(_dt(2026, 6, 3), pages=7)
        _missing_ref_over(e, _dt(2026, 6, 3), _dt(2026, 6, 25))
        self._doc(_dt(2026, 6, 4), pages=9)
        # G's not-received relationship is stamped seconds after enqueue (the
        # non-atomic intake) — still "entering with missing references".
        g_enq = _dt(2026, 6, 6)
        g = self._doc(g_enq, pages=5)
        _missing_ref_over(g, g_enq + datetime.timedelta(seconds=30), _dt(2026, 6, 20))
        june = queue_counts_rollup("month", 2, self.now)[0]
        assert june["docs_entered"] == 3
        assert june["docs_entered_missing_ref"] == 2  # E and G

    def test_missref_label_within_a_week_counts_as_entered_missing_ref(self):
        # Pre-transition, the MISSREF label is often applied a few days after
        # enqueue but reflects entry state: within a week counts, beyond doesn't.
        missref = LabelFactory(slug="MISSREF")
        h_enq = _dt(2026, 3, 5)
        h = self._doc(h_enq)
        _apply_label_over(
            h, missref, h_enq + datetime.timedelta(days=3), _dt(2026, 3, 20)
        )
        i_enq = _dt(2026, 3, 5)
        i = self._doc(i_enq)
        _apply_label_over(
            i, missref, i_enq + datetime.timedelta(days=10), _dt(2026, 3, 25)
        )
        rollup = queue_counts_rollup("month", 5, self.now)
        march = next(p for p in rollup if p["label"] == "2026-03")
        assert march["docs_entered"] == 2
        assert march["docs_entered_missing_ref"] == 1  # H only (3 days, not 10)

    def test_missing_ref_closes_on_slug_upgrade_not_only_delete(self):
        # 1g not-received refs are resolved by changing the row to refqueue in
        # place (no delete row); the interval must still close at the upgrade.
        rfc = self._doc(_dt(2026, 6, 3))
        _missing_ref_upgraded(rfc, _dt(2026, 6, 3), _dt(2026, 6, 10))
        intervals = _missing_ref_intervals_by_doc([rfc.pk])[rfc.pk]
        assert intervals == [(_dt(2026, 6, 3), _dt(2026, 6, 10))]  # closed, not open
        # It is therefore NOT blocked the whole of June, and it went to edit.
        june = queue_counts_rollup("month", 2, self.now)[0]
        assert june["docs_blocked_entire"] == 0

    def test_missing_ref_whole_period_is_blocked_entire(self):
        # A doc missing a reference the entire period counts as blocked-entire,
        # even without a blocked assignment.
        rfc = self._doc(_dt(2026, 5, 1))
        _missing_ref_over(rfc, _dt(2026, 5, 1), _dt(2026, 7, 20))
        june = queue_counts_rollup("month", 2, self.now)[0]
        assert june["docs_blocked_entire"] == 1

    def test_pages_use_historical_page_count(self):
        # Pages are read from the history record in effect when the doc entered,
        # not the current value.
        rfc = self._doc(_dt(2026, 6, 5), pages=12)
        rfc.pages = 99  # later change must NOT affect the June "pages entered"
        rfc.save()
        june = queue_counts_rollup("month", 2, self.now)[0]
        assert june["docs_entered"] == 1
        assert june["pages_entered"] == 12


class TimelineEndpointTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="timeline-user", password="pw", name="Timeline User"
        )

    def test_document_timeline_requires_auth(self):
        rfc = RfcToBeFactory()
        resp = self.client.get(
            reverse("document-assignment-timeline", args=[rfc.draft.name])
        )
        assert resp.status_code in (401, 403), resp.status_code

    def test_document_timeline_ok(self):
        self.client.force_login(self.user)
        rfc = RfcToBeFactory()
        _make_assignment(
            rfc,
            "first_editor",
            [(_dt(2026, 6, 1), "assigned"), (_dt(2026, 6, 11), "done")],
        )
        _make_assignment(
            rfc,
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        resp = self.client.get(
            reverse("document-assignment-timeline", args=[rfc.draft.name])
        )
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert "transition_date" in data
        assert "blocked_reasons" in data
        assert len(data["tracks"]) == 1  # blocked assignment is itemised elsewhere
        assert {b["kind"] for b in data["summary"]} == {KIND_BLOCKED, KIND_WORKING}

    def test_queue_stats_ok(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("stats-queue"), {"period": "month", "count": 3})
        assert resp.status_code == 200, resp.content
        assert len(resp.json()["periods"]) == 3

    def test_queue_stats_rejects_bad_period(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("stats-queue"), {"period": "decade"})
        assert resp.status_code == 400, resp.content

    def test_queue_stats_clamps_count(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("stats-queue"), {"period": "week", "count": 999})
        assert resp.status_code == 200, resp.content
        assert len(resp.json()["periods"]) == 52

    def test_queue_stats_ietf_outage_returns_503(self):
        # period=ietf needs the datatracker; a cold outage should be 503, not 500.
        from rpc import dt_v1_api_utils as dt

        dt._ietf_meetings_cache.update(at=None, data=None)  # no last-known-good
        self.client.force_login(self.user)
        with mock.patch.object(
            dt, "datatracker_api_get", side_effect=dt.DatatrackerFetchFailure
        ):
            resp = self.client.get(reverse("stats-queue"), {"period": "ietf"})
        assert resp.status_code == 503, resp.content


class IetfMeetingsCacheTests(SimpleTestCase):
    def setUp(self):
        from rpc import dt_v1_api_utils as dt

        self.dt = dt
        dt._ietf_meetings_cache.update(at=None, data=None)

    def tearDown(self):
        self.dt._ietf_meetings_cache.update(at=None, data=None)

    def test_serves_last_known_good_past_ttl_on_failure(self):
        good = {"objects": [{"number": "125", "date": "2027-11-01"}]}
        with mock.patch.object(self.dt, "datatracker_api_get", return_value=good):
            first = self.dt.datatracker_ietf_meetings()
        assert first == [("125", datetime.date(2027, 11, 1))]
        # Expire the TTL, then make the fetch fail: the stale list is served.
        self.dt._ietf_meetings_cache["at"] = time.monotonic() - 10_000
        with mock.patch.object(
            self.dt, "datatracker_api_get", side_effect=self.dt.DatatrackerFetchFailure
        ):
            again = self.dt.datatracker_ietf_meetings()
        assert again == first

    def test_raises_when_never_fetched(self):
        with mock.patch.object(
            self.dt, "datatracker_api_get", side_effect=self.dt.DatatrackerFetchFailure
        ):
            with self.assertRaises(self.dt.DatatrackerFetchFailure):
                self.dt.datatracker_ietf_meetings()
