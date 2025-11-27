# Copyright The IETF Trust 2025, All Rights Reserved
"""RFC publication support

This module is for rpc app logic related to the publish_rfc API that the front-end
calls. Note that there is a similarly named module in the datatracker app
(datatracker.utils.publication) that contains logic for making the publish API call
to datatracker.
"""
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
            "disposition is not 'in_progress'",
            code="rfctobe-bad-disposition",
        )
    if rfctobe.assignment_set.active().exclude(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document has open assignments other than publisher",
            code="rfctobe-open-assignments",
        )
    if not rfctobe.assignment_set.active().filter(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document is not assigned a publisher",
            code="rfctobe-no-publisher",
        )
    if rfctobe.finalapproval_set.count() == 0:
        raise serializers.ValidationError(
            "no final approvals have been completed",
            code="rfctobe-no-final-approvals",
        )
    if rfctobe.finalapproval_set.active().exists():
        raise serializers.ValidationError(
            "final approvals are pending",
            code="rfctobe-pending-final-approvals",
        )
    if rfctobe.rfc_number is None:
        raise serializers.ValidationError(
            "no RFC number is assigned",
            code="rfctobe-no-rfc-number",
        )



def publish_rfctobe(rfctobe: RfcToBe):
    notify_rfc_published_task.delay(rfctobe_id=rfctobe.pk)
