import datetime
import logging

import requests
import rpcapi_client
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from datatracker.models import DatatrackerPerson
from datatracker.rpcapi import with_rpcapi
from rpc.models import (
    AdditionalEmail,
    ApprovalLogMessage,
    Assignment,
    ClusterMember,
    FinalApproval,
    RfcAuthor,
    RfcToBe,
    RpcRelatedDocument,
    SubseriesMember,
    TaskRun,
)

logger = logging.getLogger(__name__)


def build_public_queue_payload() -> list:
    """Build the same payload as the pubq/queue API endpoint."""
    from rpc.api import PublicQueueList, _collect_queue_person_ids

    queryset = list(PublicQueueList.queryset.all())
    DatatrackerPerson.warm_cache(_collect_queue_person_ids(queryset))
    return PublicQueueList.serializer_class(queryset, many=True).data


def notify_datatracker_queue():
    """Push the full public queue payload to the Datatracker queue endpoint."""
    payload = build_public_queue_payload()
    logger.info("Pushing queue payload to Datatracker")

    @with_rpcapi
    def _push(*, rpcapi):
        rpcapi.process_rpc_queue(rpcapi_client.RpcQueueDataRequest(data=payload))

    _push()
    logger.info(
        "Successfully pushed queue payload to Datatracker (%d items)", len(payload)
    )


def notify_queue_precompute():
    """Notify external system about in-progress RFC changes."""

    logger.info("Notifying queue precompute system about updated RFCs")

    url = getattr(settings, "TRIGGER_QUEUE_PRECOMPUTE_URL", "")
    if not url:
        logger.warning(
            "TRIGGER_QUEUE_PRECOMPUTE_URL not configured, skipping notification"
        )
        return

    response = requests.post(
        url,
        timeout=30,
        json={},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    logger.info("Successfully notified queue precompute system about updated RFCs")


def get_updated_rfcs_since(current_check_time):
    """Return a queryset of in-queue RFCs updated since last check."""

    candidate_ids = set()

    candidate_ids.update(
        RfcToBe.history.filter(history_date__gt=current_check_time).values_list(
            "id", flat=True
        )
    )
    candidate_ids.update(
        Assignment.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )
    candidate_ids.update(
        RfcAuthor.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )
    candidate_ids.update(
        RpcRelatedDocument.history.filter(history_date__gt=current_check_time)
        .exclude(source=None)
        .values_list("source", flat=True)
    )
    candidate_ids.update(
        AdditionalEmail.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )
    doc_ids = set(
        ClusterMember.history.filter(history_date__gt=current_check_time)
        .exclude(doc=None)
        .values_list("doc", flat=True)
    )
    if doc_ids:
        candidate_ids.update(
            RfcToBe.objects.filter(draft__in=doc_ids).values_list("id", flat=True)
        )
    candidate_ids.update(
        SubseriesMember.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )
    candidate_ids.update(
        FinalApproval.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )
    candidate_ids.update(
        ApprovalLogMessage.history.filter(history_date__gt=current_check_time)
        .exclude(rfc_to_be=None)
        .values_list("rfc_to_be", flat=True)
    )

    return RfcToBe.objects.filter(pk__in=candidate_ids)


def process_rfctobe_changes_for_queue():
    """Check history tables for RFC changes since the last run and, if any exist
    and no edits occurred in the past minute, notify the queue precompute and
    datatracker endpoints (unless NOTIFY_DT_QUEUE_ENABLED is False).
    Uses a DB-level lock to prevent concurrent execution."""

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
        recent_change_threshold = current_check_time - datetime.timedelta(minutes=1)

        # Check for recent changes - if changes happened in last minute, abort
        if get_updated_rfcs_since(recent_change_threshold).exists():
            logger.info(
                "Changes detected in last minute, skipping notification to avoid "
                "notifying during active edits"
            )
            return

        # Get last successful notification time from DB
        last_check = task_run.last_run_at
        logger.info(f"Processing changes since last notification at {last_check}")

        queue_rfcs = get_updated_rfcs_since(last_check)

        if queue_rfcs.exists():
            logger.info("Sending queue precompute notification to update in-queue RFCs")
            notify_queue_precompute()
            if getattr(settings, "NOTIFY_DT_QUEUE_ENABLED", True):
                notify_datatracker_queue()
        else:
            logger.info("No in-queue RFCs changed")

        task_run.last_run_at = current_check_time
        logger.info("Completed processing history changes")

        return queue_rfcs.count()

    except Exception as e:
        logger.exception(f"Unexpected error in process_rfctobe_changes_for_queue: {e}")
        raise

    finally:
        task_run.is_running = False
        task_run.save()
