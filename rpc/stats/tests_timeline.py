# Copyright The IETF Trust 2026, All Rights Reserved
"""Tests for rpc.stats.timeline (per-document reconstruction) and the
document-timeline endpoint."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..factories import (
    LabelFactory,
    RfcToBeFactory,
)
from ..models import (
    BlockingReason,
    RfcToBeBlockingReason,
)
from . import timeline
from .test_helpers import (
    _apply_label_over,
    _dt,
    _make_assignment,
)
from .timeline import (
    KIND_AWAITING,
    KIND_BLOCKED,
    KIND_LEGACY,
    KIND_WORKING,
    TRANSITION_DATE,
    assignment_tracks,
    blocked_reason_bands,
    build_document_timeline,
    document_intervals,
)


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
            rfc_to_be=rfc,
            reason=author,
            since_when=_dt(2026, 6, 1),
            resolved=_dt(2026, 6, 5),
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc,
            reason=author,
            since_when=_dt(2026, 6, 20),
            resolved=_dt(2026, 6, 22),
        )
        RfcToBeBlockingReason.objects.create(
            rfc_to_be=rfc,
            reason=actionholder,
            since_when=_dt(2026, 6, 25),
            resolved=None,
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


class DocumentTimelineEndpointTests(TestCase):
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
