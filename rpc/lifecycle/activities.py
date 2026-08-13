# Copyright The IETF Trust 2025, All Rights Reserved
"""RfcToBe lifecycle activity modeling"""

from collections.abc import Iterable

from ..models import Assignment


class Activity:
    prereqs: Iterable["Activity"] = ()

    def pending(self, completed_activities: Iterable["Activity"]):
        """Have all prereqs been completed?"""
        return all(activity in completed_activities for activity in self.prereqs)


class CompletedAssignment(Activity):
    def __init__(self, role_slug: str, prereqs: Iterable[Activity] | None = None):
        self.role_slug = role_slug
        if prereqs is not None:
            self.prereqs = prereqs


# Formatting and reference checking run in parallel once the doc is enqueued;
# first edit waits for both.
ENQUEUER = CompletedAssignment("enqueuer")
FORMATTING = CompletedAssignment("formatting", (ENQUEUER,))
REF_CHECKER = CompletedAssignment("ref_checker", (ENQUEUER,))
FIRST_EDITOR = CompletedAssignment("first_editor", (FORMATTING, REF_CHECKER))
SECOND_EDITOR = CompletedAssignment("second_editor", (FIRST_EDITOR,))
FINAL_REVIEW_EDITOR = CompletedAssignment("final_review_editor", (SECOND_EDITOR,))
PUBLISHER = CompletedAssignment("publisher", (FINAL_REVIEW_EDITOR,))

ACTIVITIES = {
    ENQUEUER,
    FORMATTING,
    FIRST_EDITOR,
    SECOND_EDITOR,
    REF_CHECKER,
    FINAL_REVIEW_EDITOR,
    PUBLISHER,
}
ROLE_MAP = {ca.role_slug: ca for ca in ACTIVITIES}


def _assignment_states(rfctobe):
    """Get map from Activity role slug to the states of its Assignments

    Withdrawn / closed-for-hold Assignments are left out. A role may have more
    than one Assignment (one per person), so each slug maps to a list.
    """
    # Use assignments prefetched by RfcToBeQuerySet.with_activity_assignments()
    # if present to avoid a per-instance query. (Assignment.role_id is the
    # RpcRole slug and the prefetch already excludes withdrawn / closed-for-hold
    # assignments.)
    prefetched = getattr(rfctobe, "activity_assignments", None)
    if prefetched is not None:
        pairs = [(a.role_id, a.state) for a in prefetched if a.role_id in ROLE_MAP]
    else:
        pairs = (
            rfctobe.assignment_set.filter(role__slug__in=ROLE_MAP)
            .exclude(
                state__in=[Assignment.State.WITHDRAWN, Assignment.State.CLOSED_FOR_HOLD]
            )
            .values_list("role__slug", "state")
        )
    states: dict[str, list[str]] = {}
    for slug, state in pairs:
        states.setdefault(slug, []).append(state)
    return states


def _completed(states):
    """Get set of Activities whose Assignments are all done

    Takes the map returned by _assignment_states(). An Activity with a mix of
    done and still-active Assignments is not complete.
    """
    return {
        ROLE_MAP[slug]
        for slug, slug_states in states.items()
        if all(state == Assignment.State.DONE for state in slug_states)
    }


def complete_activities(rfctobe):
    """Get set of Activities that are completed for this doc"""
    return _completed(_assignment_states(rfctobe))


def incomplete_activities(rfctobe):
    """Get set of Activities that are not yet completed for this doc

    Includes those in progress / assigned and waiting for work to begin
    """
    return ACTIVITIES - complete_activities(rfctobe)


def pending_activities(rfctobe):
    """Get set of Activities waiting for assignment

    An Activity is "pending" if all its prerequisites are completed. This returns
    pending activities that don't yet have an Assignment. This logic will need
    adjustment if Activities that depend on models other than Assignment are ever
    created.
    """
    states = _assignment_states(rfctobe)
    # need an assignment for any without a non-withdrawn Assignment
    need_assignment = ACTIVITIES - {ROLE_MAP[slug] for slug in states}
    completed = _completed(states)
    return {activity for activity in need_assignment if activity.pending(completed)}
