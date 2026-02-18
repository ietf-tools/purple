# Copyright The IETF Trust 2023-2026, All Rights Reserved

"""Simple notification system for RfcToBe changes"""

from rpc.models import ASSIGNMENT_INACTIVE_STATES
from .tasks import notify_datatracker_task, notify_queue_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def notify_change(instance, change_type):
    """Notify external systems about RfcToBe changes

    Args:
        instance: The RfcToBe instance
        change_type: 'created', 'updated', or 'deleted'
    """
    # notify datatracker if disposition is 'published'
    if (
        hasattr(instance.disposition, "slug")
        and instance.disposition.slug == "published"
    ):
        notify_datatracker_task.delay(instance.pk, change_type)

    # notify if disposition is 'active' (not in inactive states)
    if (
        hasattr(instance.disposition, "slug")
        and instance.disposition.slug not in ASSIGNMENT_INACTIVE_STATES
    ):
        if not instance.draft or not instance.draft.name:
            logger.warning(
                f"RfcToBe {instance.pk} has no associated draft, skipping notification"
            )
            return
        notify_queue_task.delay(
            draft_name=instance.draft.name,
            change_type=change_type,
        )
