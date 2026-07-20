# Copyright The IETF Trust 2026, All Rights Reserved
"""Tests for rpc.stats.intervals (pure interval algebra).

These directly unit-test the functions whose logic is standalone and easy to get
wrong at the boundaries: clip, merge_intervals, split_runs_by_intervals,
overlap_seconds, first_clear_after, and active_runs. The remaining public
functions (subtract_intervals, intersect_intervals, covered_at) and the private
_merge_open_intervals are thin set operations exercised end-to-end by the
timeline and rollups suites, whose expected values would break if they were
wrong; they are not re-tested in isolation here.
"""

from django.test import SimpleTestCase

from .intervals import (
    active_runs,
    clip,
    first_clear_after,
    merge_intervals,
    overlap_seconds,
    split_runs_by_intervals,
)
from .test_helpers import dt


class PureHelperTests(SimpleTestCase):
    def test_clip_within_bounds(self):
        assert clip(dt(2026, 6, 1), dt(2026, 6, 10)) == (
            dt(2026, 6, 1),
            dt(2026, 6, 10),
        )

    def test_clip_lo_trims_start(self):
        assert clip(dt(2026, 5, 1), dt(2026, 6, 1), lo=dt(2026, 5, 20)) == (
            dt(2026, 5, 20),
            dt(2026, 6, 1),
        )

    def test_clip_hi_trims_open_end(self):
        assert clip(dt(2026, 5, 1), None, hi=dt(2026, 5, 20)) == (
            dt(2026, 5, 1),
            dt(2026, 5, 20),
        )

    def test_clip_empty_returns_none(self):
        assert clip(dt(2026, 6, 1), dt(2026, 7, 1), lo=dt(2026, 7, 1)) is None

    def test_merge_overlapping_and_open(self):
        now = dt(2026, 6, 30)
        merged = merge_intervals(
            [
                (dt(2026, 6, 1), dt(2026, 6, 10)),
                (dt(2026, 6, 5), dt(2026, 6, 12)),
                (dt(2026, 6, 20), None),
            ],
            now,
        )
        assert merged == [
            (dt(2026, 6, 1), dt(2026, 6, 12)),
            (dt(2026, 6, 20), now),
        ]

    def test_overlap_seconds_clips_to_window(self):
        seconds = overlap_seconds(
            [(dt(2026, 6, 1), dt(2026, 6, 11))],
            dt(2026, 6, 5),
            dt(2026, 7, 1),
        )
        assert seconds == 6 * 24 * 3600

    def test_split_runs_by_intervals(self):
        now = dt(2026, 6, 30)
        # A closed run straddling one interval, and an open-ended run that the
        # helper must treat as ending at ``now``.
        inside, outside = split_runs_by_intervals(
            [
                (dt(2026, 6, 1), dt(2026, 6, 20), "x"),
                (dt(2026, 6, 25), None, "y"),
            ],
            [(dt(2026, 6, 5), dt(2026, 6, 10)), (dt(2026, 6, 26), dt(2026, 6, 28))],
            now,
        )
        assert inside == [
            (dt(2026, 6, 5), dt(2026, 6, 10)),
            (dt(2026, 6, 26), dt(2026, 6, 28)),
        ]
        assert outside == [
            (dt(2026, 6, 1), dt(2026, 6, 5)),
            (dt(2026, 6, 10), dt(2026, 6, 20)),
            (dt(2026, 6, 25), dt(2026, 6, 26)),
            (dt(2026, 6, 28), now),
        ]

    def test_first_clear_after(self):
        d1, d2, d3 = dt(2026, 1, 1), dt(2026, 2, 1), dt(2026, 3, 1)
        d4 = dt(2026, 4, 1)
        assert first_clear_after([], d2) == d2  # never missing -> clear at enqueue
        assert first_clear_after([(d1, d3)], d2) == d3  # inside -> clears at end
        assert first_clear_after([(d1, None)], d2) is None  # ongoing -> never clears
        assert first_clear_after([(d3, d4)], d2) == d2  # missing starts later
        assert first_clear_after([(d1, d2), (d3, d4)], d2) == d2  # clear in the gap

    def test_active_runs_split_by_inactive(self):
        class Rec:
            def __init__(self, state, when):
                self.state = state
                self.history_date = when

        runs = active_runs(
            [
                Rec("assigned", dt(2026, 6, 1)),
                Rec("closed_for_hold", dt(2026, 6, 5)),
                Rec("in_progress", dt(2026, 6, 8)),
                Rec("done", dt(2026, 6, 11)),
            ]
        )
        assert runs == [
            (dt(2026, 6, 1), dt(2026, 6, 5), "assigned"),
            (dt(2026, 6, 8), dt(2026, 6, 11), "in_progress"),
        ]

    def test_active_runs_open_ended(self):
        class Rec:
            def __init__(self, state, when):
                self.state = state
                self.history_date = when

        runs = active_runs([Rec("in_progress", dt(2026, 6, 1))])
        assert runs == [(dt(2026, 6, 1), None, "in_progress")]
