# Copyright The IETF Trust 2025, All Rights Reserved
"""RfcToBe lifecycle modeling"""

from collections.abc import Iterable

from .models import Assignment


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


ENQUEUER = CompletedAssignment("enqueuer")
FORMATTING = CompletedAssignment("formatting", (ENQUEUER,))
FIRST_EDITOR = CompletedAssignment("first_editor", (FORMATTING,))
SECOND_EDITOR = CompletedAssignment("second_editor", (FIRST_EDITOR,))
REF_CHECKER = CompletedAssignment("ref_checker", (FORMATTING,))
FINAL_REVIEW_EDITOR = CompletedAssignment(
    "final_review_editor", (SECOND_EDITOR, REF_CHECKER)
)
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


# todo: implement these for non-assignment activities (or simplify)
def complete_activities(rfctobe):
    """Get set of Activities that are completed for this doc"""
    role_map = {ca.role_slug: ca for ca in ACTIVITIES}
    completed_slugs = rfctobe.assignment_set.filter(
        state=Assignment.State.DONE,
        role__slug__in=role_map,
    ).values_list("role__slug", flat=True)
    return {role_map[slug] for slug in completed_slugs}


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
    role_map = {ca.role_slug: ca for ca in ACTIVITIES}
    # Get map from role slug to state
    state_map = dict(
        rfctobe.assignment_set.filter(role__slug__in=role_map)
        .exclude(state=Assignment.State.WITHDRAWN)
        .values_list("role__slug", "state")
    )
    # need an assignment for any without a non-withdrawn Assignment
    need_assignment = ACTIVITIES - {role_map[slug] for slug in state_map}
    completed = {
        role_map[slug]
        for slug, state in state_map.items()
        if state == Assignment.State.DONE
    }
    return {activity for activity in need_assignment if activity.pending(completed)}
