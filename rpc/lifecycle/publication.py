# Copyright The IETF Trust 2025, All Rights Reserved
"""RFC publication support"""
from rpcauth.models import User
from ..models import RfcToBe
from datatracker.tasks import notify_rfc_published_task


def can_publish(rfctobe: RfcToBe, user: User):
    if user.is_superuser:
        return True
    rpcperson = user.rpcperson()
    if rpcperson is None:
        return False
    return rpcperson.assignment_set.active().filter(
        rfc_to_be=rfctobe,
        role__slug="publisher",
    ).exists()


def is_ready_to_publish(rfctobe: RfcToBe):
    return True  # todo validate state


def publish_rfctobe(rfctobe: RfcToBe):
    notify_rfc_published_task.delay(rfctobe_id=rfctobe.pk)
