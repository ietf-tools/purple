# Copyright The IETF Trust 2025, All Rights Reserved
"""RfcToBe lifecycle modeling"""
from functools import cached_property

from django.db.models import Q


class Activity:
    def completed_as_q(self):
        raise NotImplementedError("Subclasses must implement this")


class CompletedAssignment(Activity):
    def __init__(self, role_slug: str):
        self.role_slug = role_slug

    def completed_as_q(self):
        return Q(
            assignment__role__slug=self.role_slug,
            assignment__state="done"
        )


ACTIVITIES = (
    CompletedAssignment("formatting"),
    CompletedAssignment("first_editor"),
    CompletedAssignment("second_editor"),
    CompletedAssignment("ref_checker"),
    CompletedAssignment("final_review_editor"),
    CompletedAssignment("publisher"),
)


def incomplete_activities(rfctobe):
    interesting_roles = [ca.role_slug for ca in ACTIVITIES]
    completed_assignments = rfctobe.assignment_set.filter(
        state="done",
        role__slug__in=interesting_roles,
    ).values_list("role__slug", flat=True)
    return [
        activity
        for activity in ACTIVITIES
        if activity.role_slug not in completed_assignments
    ]
