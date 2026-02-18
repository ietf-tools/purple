# Copyright The IETF Trust 2025-2026, All Rights Reserved
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F

from datatracker.utils.publication import publish_rfc_metadata
from utils.task_utils import RetryTask

from .lifecycle.metadata import Metadata
from .lifecycle.publication import (
    PublicationError,
    TemporaryPublicationError,
    publish_rfctobe,
)
from .lifecycle.repo import GithubRepository
from .models import MailMessage, MetadataValidationResults, RfcToBe

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
def notify_queue_task(self, draft_name, change_type):
    """Notify external queue system about in-progress RFC changes

    Args:
        draft_name: Draft name (if available)
        change_type: 'created', 'updated', or 'deleted'
    """
    logger.info(f"Notifying queue system about draft {draft_name} ({change_type})")

    url = getattr(settings, "QUEUE_NOTIFICATION_URL", "")
    if not url:
        logger.warning("QUEUE_NOTIFICATION_URL not configured, skipping notification")
        return

    payload = {
        "draft_name": draft_name,
        "change_type": change_type,
    }

    # try:
    #     response = requests.post(
    #         url,
    #         json=payload,
    #         timeout=30,
    #         headers={'Content-Type': 'application/json'},
    #     )
    #     response.raise_for_status()
    #     logger.info(
    #         f"Successfully notified datatracker system about draft {draft_name} "
    #         f"({change_type})"
    #     )
    # except requests.RequestException as exc:
    #     logger.error(
    #         f"Failed to notify datatracker system about draft {draft_name}: {exc}"
    #     )
    #     # Retry with exponential backoff
    #     raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task(bind=True, max_retries=5)
def notify_datatracker_task(self, rfctobe_id, change_type):
    """Notify datatracker about published RFC changes

    Args:
        rfctobe_id: Primary key of the RfcToBe instance
        change_type: 'created', 'updated', or 'deleted'
    """
    try:
        rfc_to_be = RfcToBe.objects.get(pk=rfctobe_id)
    except RfcToBe.DoesNotExist:
        logger.error(f"RfcToBe with id {rfctobe_id} does not exist")
        return

    logger.info(
        f"Notifying datatracker about RFC {rfc_to_be.rfc_number} ({change_type})"
    )

    try:
        publish_rfc_metadata(rfc_to_be)
        logger.info(
            f"Notified datatracker about updates in published RFC "
            f"{rfc_to_be.rfc_number}"
        )
    except Exception as exc:
        logger.error(
            f"Failed to notify datatracker about RFC {rfc_to_be.rfc_number}: {exc}"
        )
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
