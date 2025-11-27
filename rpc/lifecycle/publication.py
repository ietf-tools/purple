# Copyright The IETF Trust 2025, All Rights Reserved
"""RFC publication support"""
from rest_framework import serializers

from rpcauth.models import User
from ..models import RfcToBe
from datatracker.tasks import notify_rfc_published_task


def can_publish(rfctobe: RfcToBe, user: User):
    """Can this user publish this RfcToBe?

    Does not evaluate whether the RfcToBe is ready to be published.
    """
    if user.is_superuser:
        return True
    rpcperson = user.rpcperson()
    if rpcperson is None:
        return False
    return rpcperson.assignment_set.active().filter(
        rfc_to_be=rfctobe,
        role__slug="publisher",
    ).exists()


def validate_ready_to_publish(rfctobe: RfcToBe):
    """Is this RfcToBe ready to be published?

    No return value. Raises serializers.ValidationError if not ready.
    """
    if rfctobe.disposition_id != "in_progress":
        raise serializers.ValidationError(
            "disposition is not 'in_progress'"
        )
    if rfctobe.assignment_set.active().exclude(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document has open assignments other than publisher"
        )
    if not rfctobe.assignment_set.active().filter(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document is not assigned a publisher"
        )
    if rfctobe.finalapproval_set.count() == 0:
        raise serializers.ValidationError(
            "no final approvals have been completed"
        )
    if rfctobe.finalapproval_set.active().exists():
        raise serializers.ValidationError(
            "final approvals are pending"
        )
    if rfctobe.rfc_number is None:
        raise serializers.ValidationError(
            "no RFC number is assigned"
        )



def publish_rfctobe(rfctobe: RfcToBe):
    notify_rfc_published_task.delay(rfctobe_id=rfctobe.pk)
