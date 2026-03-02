import logging

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rpc.models import (
    AdditionalEmail,
    Assignment,
    ClusterMember,
    RfcAuthor,
    RfcToBe,
    RpcRelatedDocument,
    SubseriesMember,
    TaskRun,
)

logger = logging.getLogger(__name__)


def notify_red_precompute(rfctobe_ids):
    """Notify external system about in-progress RFC changes."""

    logger.info(f"Notifying RED precompute system about RFCs: {rfctobe_ids}")

    url = getattr(settings, "TRIGGER_RED_PRECOMPUTE_URL", "")
    if not url:
        logger.warning(
            "TRIGGER_RED_PRECOMPUTE_URL not configured, skipping notification"
        )
        return

    payload = {
        "rfcs": ",".join(str(n) for n in sorted(rfctobe_ids)),
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    logger.info(
        f"Successfully notified RED precompute system about RFCs: {rfctobe_ids}"
    )


def get_updated_rfcs_since(current_check_time):
    """Helper function to get IDs of in-progress RFCs updated since last check"""

    def _should_notify_queue(rfc):
        """Check if RFC should be included in queue notifications"""

        return rfc and rfc.disposition and rfc.disposition.slug == "in_progress"

    # Track affected RFCs for queue notifications (in_progress RFCs)
    queue_rfcs = set()

    # Check RfcToBe direct changes
    for hist in RfcToBe.history.filter(
        history_date__gt=current_check_time
    ).select_related("disposition", "draft"):
        if _should_notify_queue(hist):
            queue_rfcs.add(hist.id)

    # Check Assignment changes
    for hist in Assignment.history.filter(
        history_date__gt=current_check_time
    ).select_related("rfc_to_be__disposition"):
        if _should_notify_queue(hist.rfc_to_be):
            queue_rfcs.add(hist.rfc_to_be.id)

    # Check RfcAuthor changes
    for hist in RfcAuthor.history.filter(
        history_date__gt=current_check_time
    ).select_related("rfc_to_be__disposition"):
        if _should_notify_queue(hist.rfc_to_be):
            queue_rfcs.add(hist.rfc_to_be.id)

    # Check RpcRelatedDocument changes
    for hist in RpcRelatedDocument.history.filter(
        history_date__gt=current_check_time
    ).select_related("source", "source__disposition"):
        if _should_notify_queue(hist.source):
            queue_rfcs.add(hist.source.id)

    # Check AdditionalEmail changes
    for hist in AdditionalEmail.history.filter(
        history_date__gt=current_check_time
    ).select_related("rfc_to_be__disposition"):
        if _should_notify_queue(hist.rfc_to_be):
            queue_rfcs.add(hist.rfc_to_be.id)

    # Check ClusterMembership changes
    for hist in ClusterMember.history.filter(
        history_date__gt=current_check_time
    ).select_related("doc"):
        rfcs = RfcToBe.objects.filter(draft=hist.doc).select_related("disposition")
        for rfc in rfcs:
            if _should_notify_queue(rfc):
                queue_rfcs.add(rfc.id)

    # Check SubseriesMember changes
    for hist in SubseriesMember.history.filter(
        history_date__gt=current_check_time
    ).select_related("rfc_to_be__disposition"):
        if _should_notify_queue(hist.rfc_to_be):
            queue_rfcs.add(hist.rfc_to_be.id)

    return queue_rfcs


def get_recent_changes(check_time):
    """Check if any relevant changes have occurred since the check time"""

    recent_change_threshold = check_time - timezone.timedelta(minutes=1)

    return (
        RfcToBe.history.filter(history_date__gt=recent_change_threshold).exists()
        or Assignment.history.filter(history_date__gt=recent_change_threshold).exists()
        or RfcAuthor.history.filter(history_date__gt=recent_change_threshold).exists()
        or RpcRelatedDocument.history.filter(
            history_date__gt=recent_change_threshold
        ).exists()
        or AdditionalEmail.history.filter(
            history_date__gt=recent_change_threshold
        ).exists()
        or ClusterMember.history.filter(
            history_date__gt=recent_change_threshold
        ).exists()
        or SubseriesMember.history.filter(
            history_date__gt=recent_change_threshold
        ).exists()
    )


def process_rfctobe_changes_for_queue():
    """Poll history tables and send batched notification to queue system about
    in-progress RFC changes"""

    logger.info("Processing RfcToBe changes from history")

    current_check_time = timezone.now()

    with transaction.atomic():
        task_run, _ = TaskRun.objects.select_for_update().get_or_create(
            task_name="process_rfctobe_changes_for_queue",
            defaults={"last_run_at": current_check_time, "is_running": False},
        )
        if task_run.is_running:
            logger.info("Task is already running, skipping this execution")
            return
        task_run.is_running = True
        task_run.save()

    try:
        recent_change_threshold = current_check_time - timezone.timedelta(minutes=1)

        # Check for recent changes - if changes happened in last minute, abort
        recent_changes_exist = get_recent_changes(recent_change_threshold)

        if recent_changes_exist:
            logger.info(
                "Changes detected in last minute, skipping notification to avoid "
                "notifying during active edits"
            )
            return

        # Get last successful notification time from DB
        last_check = task_run.last_run_at
        logger.info(f"Processing changes since last notification at {last_check}")

        queue_rfcs = get_updated_rfcs_since(last_check)

        if queue_rfcs:
            logger.info(
                f"Sending batched RED precompute notification for {len(queue_rfcs)} "
                "RFCs"
            )
            notify_red_precompute(list(queue_rfcs))
        else:
            logger.info("No in-progress RFCs changed")

        task_run.last_run_at = current_check_time
        logger.info("Completed processing history changes")

    except Exception as e:
        logger.exception(f"Unexpected error in process_rfctobe_changes_for_queue: {e}")
        raise

    finally:
        task_run.is_running = False
        task_run.save()
