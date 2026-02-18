# Copyright The IETF Trust 2023-2026, All Rights Reserved

"""Simple notification system for RfcToBe changes"""

from .tasks import notify_errata


def notify_change(instance, change_type):
    """Notify external systems about RfcToBe changes

    Args:
        instance: The RfcToBe instance
        change_type: 'created', 'updated', or 'deleted'
    """
    # Only notify if disposition is 'published'
    if hasattr(instance.disposition, 'slug') and instance.disposition.slug == 'published':
        notify_errata.delay(
            rfc_number=instance.rfc_number,
            draft_name=instance.draft.name if instance.draft else None,
            change_type=change_type,
        )
