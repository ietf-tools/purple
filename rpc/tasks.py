# Copyright The IETF Trust 2025-2026, All Rights Reserved
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from utils.task_utils import RetryTask

from .lifecycle.metadata import Metadata
from .lifecycle.publication import (
    PublicationError,
    TemporaryPublicationError,
    publish_rfctobe,
)
from .lifecycle.repo import GithubRepository
from .models import (
    AdditionalEmail,
    Assignment,
    ClusterMember,
    MailMessage,
    MetadataValidationResults,
    PeriodicTaskRun,
    RfcAuthor,
    RfcToBe,
    RpcRelatedDocument,
    SubseriesMember,
)

logger = get_task_logger(__name__)


class EmailTask(RetryTask):
    max_retries = 4 * 24 * 3  # every 15 minutes for 3 days
    # When retries run out, the admins will be emailed. There's a good chance that
    # sending that mail will fail also, but it's what we have for now.


class SendEmailError(Exception):
    pass


@shared_task(base=EmailTask, autoretry_for=(SendEmailError,))
def send_mail_task(message_id):
    message = MailMessage.objects.get(pk=message_id)
    email = message.as_emailmessage()
    try:
        email.send()
    except Exception as err:
        logger.error(
            "Sending with subject '%s' failed: %s",
            message.subject,
            str(err),
        )
        raise SendEmailError from err
    else:
        # Flag that the message was sent in case the task fails before deleting it
        MailMessage.objects.filter(pk=message_id).update(sent=True)
    finally:
        # Always increment this
        MailMessage.objects.filter(pk=message_id).update(attempts=F("attempts") + 1)
    # Get friendly name of msgtype
    message_type = dict(MailMessage.MessageType.choices)[message.msgtype]
    comment = f"Sent {message_type} email with Message-ID={message.message_id}"
    if message.rfctobe is not None:
        message.rfctobe.rpcdocumentcomment_set.create(
            comment=comment,
            by=message.sender,
        )
    if message.draft is not None:
        message.draft.rpcdocumentcomment_set.create(
            comment=comment,
            by=message.sender,
        )
    message.delete()


@shared_task(bind=True)
def validate_metadata_task(self, rfc_to_be_id):
    """
    Celery task to fetch repo, manifest, parse XML, and store metadata validation
    results.
    """

    def _save_metadata_results(rfc_to_be, head_sha, metadata, status, detail=None):
        """Helper to save metadata validation results"""
        if rfc_to_be is not None:
            mvr = MetadataValidationResults.objects.get(rfc_to_be=rfc_to_be)
            mvr.head_sha = head_sha
            mvr.metadata = metadata
            mvr.status = status
            mvr.detail = detail
            mvr.save()

    head_sha = None
    metadata = None
    rfc_to_be = None

    try:
        rfc_to_be = RfcToBe.objects.get(pk=rfc_to_be_id)
        repo_url = rfc_to_be.repository
        rfc_number = rfc_to_be.rfc_number
        if not repo_url:
            status = MetadataValidationResults.Status.FAILED
            detail = f"No repository URL for RfcToBe {rfc_to_be_id}"
            logger.error(detail)
            _save_metadata_results(rfc_to_be, head_sha, metadata, status, detail)
            return

        repo = GithubRepository(repo_url)
        head_sha = repo.ref  # gets current head + guarantees all files from same ref

        # if sha unchanged, skip processing
        existing = MetadataValidationResults.objects.filter(
            rfc_to_be=rfc_to_be, head_sha=head_sha
        ).first()
        if existing:
            logger.info(
                f"Metadata already stored for RfcToBe {rfc_to_be_id} at SHA {head_sha}"
            )
            return

        manifest = repo.get_manifest()
        # Find XML file path
        xml_path = None
        for pub in manifest.get("publications", []):
            if pub.get("rfcNumber") == rfc_number:
                for f in pub.get("files", []):
                    if f.get("type", "").lower() == "xml":
                        xml_path = f.get("path")
                        break

        if not xml_path:
            status = MetadataValidationResults.Status.FAILED
            detail = f"No XML file found in manifest for RFC {rfc_number}"
            logger.error(detail)
            _save_metadata_results(rfc_to_be, head_sha, metadata, status, detail)
            return

        xml_file = repo.get_file(xml_path)
        xml_bytes = b"".join(chunk for chunk in xml_file.chunks())
        xml_string = xml_bytes.decode("utf-8")
        metadata = Metadata.parse_rfc_xml(xml_string)
        status = MetadataValidationResults.Status.SUCCESS
        logger.info(f"Metadata validation complete for RfcToBe {rfc_to_be_id}")
        _save_metadata_results(rfc_to_be, head_sha, metadata, status)

    except Exception as e:
        logger.exception(f"Error in validate_metadata_task for RfcToBe {rfc_to_be_id}")
        detail = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
        status = MetadataValidationResults.Status.FAILED
        _save_metadata_results(rfc_to_be, head_sha, metadata, status, detail)


class PublishRfcToBeTask(RetryTask):
    pass


@shared_task(
    bind=True,
    base=PublishRfcToBeTask,
    throws=(RfcToBe.DoesNotExist, PublicationError),
    autoretry_for=(TemporaryPublicationError,),
)
def publish_rfctobe_task(self, rfctobe_id, expected_head):
    rfctobe = RfcToBe.objects.get(pk=rfctobe_id)
    publish_rfctobe(rfctobe, expected_head=expected_head)


@shared_task(bind=True, max_retries=5)
def notify_queue_task(self, rfctobe_ids):
    """Notify external queue system about in-progress RFC changes

    Args:
        rfctobe_ids: List of RfcToBe primary keys
        current_check_time: Timestamp when this notification was triggered
    """
    logger.info(f"Notifying queue system about RFCs: {rfctobe_ids}")

    url = getattr(settings, "QUEUE_NOTIFICATION_URL", "")
    if not url:
        logger.warning("QUEUE_NOTIFICATION_URL not configured, skipping notification")
        return

    payload = {
        "rfcs": ", ".join(str(n) for n in sorted(rfctobe_ids)),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        logger.info(f"Successfully notified queue system about RFCs: {rfctobe_ids}")

        # Update last successful run timestamp
        PeriodicTaskRun.objects.update_or_create(
            task_name="notify_queue",
            defaults={"last_run_at": timezone.now(), "is_running": False},
        )
    except requests.RequestException as exc:
        logger.error(
            f"Failed to notify queue system about RFCs {rfctobe_ids}: {exc} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1})"
        )

        if self.request.retries >= self.max_retries:
            logger.critical(
                f"Exhausted retries for queue notification. "
                f"RFCs {rfctobe_ids} were not notified."
            )
            # Mark as not running to unblock the periodic task
            PeriodicTaskRun.objects.filter(
                task_name="process_rfctobe_changes_from_history"
            ).update(is_running=False)
            return

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries)) from exc


@shared_task(bind=True)
def process_rfctobe_changes_from_history(self):
    """Poll history tables and send batched notifications for changes
    (runs every minute)"""

    logger.info("Processing RfcToBe changes from history")

    current_check_time = timezone.now()

    # Check if task is already running
    try:
        task_run = PeriodicTaskRun.objects.get(
            task_name="process_rfctobe_changes_from_history"
        )
        if task_run.is_running:
            logger.info("Task is already running, skipping this execution")
            return
        task_run.is_running = True
        task_run.save()
    except PeriodicTaskRun.DoesNotExist:
        # First run - create the record
        task_run = PeriodicTaskRun.objects.create(
            task_name="process_rfctobe_changes_from_history",
            last_run_at=current_check_time,
            is_running=True,
        )

    try:
        recent_change_threshold = current_check_time - timezone.timedelta(minutes=1)

        # Check for recent changes - if changes happened in last minute, abort
        recent_changes_exist = (
            RfcToBe.history.filter(history_date__gt=recent_change_threshold).exists()
            or Assignment.history.filter(
                history_date__gt=recent_change_threshold
            ).exists()
            or RfcAuthor.history.filter(
                history_date__gt=recent_change_threshold
            ).exists()
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

        if recent_changes_exist:
            logger.info(
                "Changes detected in last minute, skipping notification to avoid "
                "notifying during active edits"
            )
            task_run.is_running = False
            task_run.save()
            return

        # Get last successful notification time from DB
        last_check = task_run.last_run_at
        logger.info(f"Processing changes since last notification at {last_check}")

        def _should_notify_queue(rfc):
            """Check if RFC should be included in queue notifications"""
            return rfc and rfc.disposition and rfc.disposition.slug == "in_progress"

        # Track affected RFCs for queue notifications (in_progress RFCs)
        queue_rfcs = set()

        # Check RfcToBe direct changes
        for hist in RfcToBe.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("disposition", "draft"):
            if _should_notify_queue(hist):
                queue_rfcs.add(hist.id)

        # Check Assignment changes
        for hist in Assignment.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("rfc_to_be__disposition"):
            if _should_notify_queue(hist.rfc_to_be):
                queue_rfcs.add(hist.rfc_to_be.id)

        # Check RfcAuthor changes
        for hist in RfcAuthor.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("rfc_to_be__disposition"):
            if _should_notify_queue(hist.rfc_to_be):
                queue_rfcs.add(hist.rfc_to_be.id)

        # Check RpcRelatedDocument changes
        for hist in RpcRelatedDocument.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("source", "source__disposition"):
            if _should_notify_queue(hist.source):
                queue_rfcs.add(hist.source.id)

        # Check AdditionalEmail changes
        for hist in AdditionalEmail.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("rfc_to_be__disposition"):
            if _should_notify_queue(hist.rfc_to_be):
                queue_rfcs.add(hist.rfc_to_be.id)

        # Check ClusterMembership changes
        for hist in ClusterMember.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("doc"):
            rfcs = RfcToBe.objects.filter(draft=hist.doc).select_related("disposition")
            for rfc in rfcs:
                if _should_notify_queue(rfc):
                    queue_rfcs.add(rfc.id)

        # Check SubseriesMember changes
        for hist in SubseriesMember.history.filter(
            history_date__gt=last_check, history_date__lte=current_check_time
        ).select_related("rfc_to_be__disposition"):
            if _should_notify_queue(hist.rfc_to_be):
                queue_rfcs.add(hist.rfc_to_be.id)

        if queue_rfcs:
            logger.info(
                f"Sending batched queue notification for {len(queue_rfcs)} RFCs"
            )
            notify_queue_task.delay(list(queue_rfcs))
        else:
            logger.info("No in-progress RFCs changed")

        task_run.last_run_at = current_check_time
        task_run.is_running = False
        task_run.save()

        logger.info("Completed processing history changes")

    except Exception as e:
        logger.exception(
            f"Unexpected error in process_rfctobe_changes_from_history: {e}"
        )
