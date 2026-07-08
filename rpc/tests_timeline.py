# Copyright The IETF Trust 2026, All Rights Reserved
"""Tests for rpc.lifecycle.timeline and the timeline/queue-stats endpoints."""

import datetime

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
    KIND_BLOCKED,
    KIND_LEGACY,
    KIND_WORKING,
    TRANSITION_DATE,
    _active_runs,
    _candidate_docs,
    _clip,
    _merge_intervals,
    _overlap_seconds,
    build_document_timeline,
    document_intervals,
    period_windows,
    queue_rollup,
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
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        payload = build_document_timeline(rfc, self.now)
        assert payload["transition_date"] == TRANSITION_DATE
        assert {b.kind for b in payload["summary"]} == {KIND_BLOCKED, KIND_WORKING}
        assert len(payload["tracks"]) == 1


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
        # Time accrued as of the period end, broken out per role.
        assert june["total_working_seconds"] == 10 * 24 * 3600
        assert june["total_blocked_seconds"] == 3 * 24 * 3600
        by_role = {r["role"]: r for r in june["by_role"]}
        assert by_role["first_editor"]["is_blocked"] is False
        assert by_role["first_editor"]["seconds"] == 10 * 24 * 3600
        assert by_role["blocked"]["is_blocked"] is True
        assert by_role["blocked"]["seconds"] == 3 * 24 * 3600
        assert june["legacy_included"] is False

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
            "blocked",
            [(_dt(2026, 6, 15), "in_progress"), (_dt(2026, 6, 18), "done")],
        )
        resp = self.client.get(
            reverse("document-assignment-timeline", args=[rfc.draft.name])
        )
        assert resp.status_code == 200, resp.content
        data = resp.json()
        assert "transition_date" in data
        assert len(data["tracks"]) == 1
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
