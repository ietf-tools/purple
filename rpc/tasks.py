# Copyright The IETF Trust 2025, All Rights Reserved
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F

from rpc.lifecycle.metadata import Metadata
from rpc.lifecycle.repo import GithubRepository
from rpc.models import MailMessage, MetadataValidationResults, RfcToBe
from utils.task_utils import RetryTask

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
    try:
        rfc_to_be = RfcToBe.objects.get(pk=rfc_to_be_id)
        repo_url = rfc_to_be.repository
        rfc_number = rfc_to_be.rfc_number
        if not repo_url:
            logger.error(f"No repository URL for RfcToBe {rfc_to_be_id}")
            return {"error": "No repository URL set for this RfcToBe."}
        repo = GithubRepository(repo_url)
        head_sha = repo.get_head_sha()

        # if sha unchanged, skip processing
        existing = MetadataValidationResults.objects.filter(
            rfc_to_be=rfc_to_be, head_sha=head_sha
        ).first()
        if existing:
            logger.info(
                f"Metadata already stored for RfcToBe {rfc_to_be_id} at SHA {head_sha}"
            )
            return {"status": "unchanged", "id": existing.id}

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
            logger.error(f"No XML file found in manifest for RFC {rfc_number}")
            return {"error": "No XML file found in manifest for this RFC number."}
        xml_file = repo.get_file(xml_path)
        xml_bytes = b"".join(chunk for chunk in xml_file.chunks())
        xml_string = xml_bytes.decode("utf-8")
        metadata = Metadata.parse_rfc_xml(xml_string)

        # Update the existing record
        mvr = MetadataValidationResults.objects.get(rfc_to_be=rfc_to_be)
        mvr.head_sha = head_sha
        mvr.metadata = metadata
        mvr.is_pending = False
        mvr.save()

        logger.info(f"Metadata validation complete for RfcToBe {rfc_to_be_id}")
        return {"status": "success", "id": mvr.id}
    except Exception as e:
        logger.error(f"Error in validate_metadata_task: {e}")
        return {"error": str(e)}
