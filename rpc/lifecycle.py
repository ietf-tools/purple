# Copyright The IETF Trust 2025, All Rights Reserved
"""RfcToBe lifecycle modeling"""

from collections.abc import Iterable

from django.db.models import Q


class Activity:
    prereqs: Iterable["Activity"] = ()

    def completed_as_q(self):
        raise NotImplementedError("Subclasses must implement this")

    def pending(self, completed_activities: Iterable["Activity"]):
        return all(activity in completed_activities for activity in self.prereqs)


class CompletedAssignment(Activity):
    def __init__(self, role_slug: str, prereqs: Iterable[Activity] | None = None):
        self.role_slug = role_slug
        if prereqs is not None:
            self.prereqs = prereqs

    def completed_as_q(self):
        return Q(assignment__role__slug=self.role_slug, assignment__state="done")


FORMATTING = CompletedAssignment("formatting")
FIRST_EDITOR = CompletedAssignment("first_editor", (FORMATTING,))
SECOND_EDITOR = CompletedAssignment("second_editor", (FIRST_EDITOR,))
REF_CHECKER = CompletedAssignment("ref_checker", (FORMATTING,))
FINAL_REVIEW_EDITOR = CompletedAssignment(
    "final_review_editor", (SECOND_EDITOR, REF_CHECKER)
)
PUBLISHER = CompletedAssignment("publisher", (FINAL_REVIEW_EDITOR,))

ACTIVITIES = {
    FORMATTING,
    FIRST_EDITOR,
    SECOND_EDITOR,
    REF_CHECKER,
    FINAL_REVIEW_EDITOR,
    PUBLISHER,
}


# todo: implement these for non-assignment activities (or simplify)
def complete_activities(rfctobe):
    role_map = {ca.role_slug: ca for ca in ACTIVITIES}
    completed_slugs = rfctobe.assignment_set.filter(
        state="done",
        role__slug__in=role_map,
    ).values_list("role__slug", flat=True)
    return {role_map[slug] for slug in completed_slugs}


def incomplete_activities(rfctobe):
    return ACTIVITIES - complete_activities(rfctobe)


def pending_activities(rfctobe):
    completed = complete_activities(rfctobe)
    return {
        activity for activity in ACTIVITIES - completed if activity.pending(completed)
    }
