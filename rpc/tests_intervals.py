# Copyright The IETF Trust 2026, All Rights Reserved
"""Tests for rpc.lifecycle.intervals (pure interval algebra)."""

from django.test import SimpleTestCase

from .lifecycle.intervals import (
    _active_runs,
    _clip,
    _first_clear_after,
    _merge_intervals,
    _overlap_seconds,
)
from .lifecycle_test_helpers import _dt


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
