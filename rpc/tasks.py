# Copyright The IETF Trust 2025-2026, All Rights Reserved
import rpcapi_client
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F

from datatracker.models import Document
from datatracker.rpcapi import with_rpcapi
from rpc.lifecycle.blocked_assignments import apply_blocked_assignment_for_rfc
from utils.task_utils import RetryTask

from .lifecycle.metadata import Metadata
from .lifecycle.notifications import process_rfctobe_changes_for_queue
from .lifecycle.publication import (
    PublicationError,
    TemporaryPublicationError,
    publish_rfctobe,
)
from .lifecycle.repo import GithubRepository
from .models import (
    DocRelationshipName,
    MailMessage,
    MetadataValidationResults,
    RfcToBe,
    RpcRelatedDocument,
)
from .rfcindex import refresh_rfc_index
from .utils import get_or_create_draft_by_name


@shared_task
def set_stream_manager_task(rfc_to_be_id: int):
    """Resolve and persist the stream_manager FK for a RfcToBe."""
    try:
        rfctobe = RfcToBe.objects.get(pk=rfc_to_be_id)
    except RfcToBe.DoesNotExist:
        logger.warning("set_stream_manager_task: RfcToBe pk=%s not found", rfc_to_be_id)
        return
    if rfctobe.stream_manager_id is not None:
        return
    person = rfctobe.resolve_stream_manager_person()
    RfcToBe.objects.filter(pk=rfc_to_be_id).update(stream_manager=person)


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
        logger.error(f"Error in validate_metadata_task: {e}")
        detail = str(e)
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


@shared_task
def process_rfctobe_changes_for_queue_task():
    """Check for changes to in-progress RFCs and send notifications"""
    try:
        process_rfctobe_changes_for_queue()
    except Exception as e:
        logger.error(f"Error in process_rfctobe_changes_for_queue_task: {e}")


@shared_task
def refresh_rfc_index_task():
    refresh_rfc_index()


@shared_task
def update_blocked_assignments_for_in_progress_rfcs_task():
    """Process all in_progress RfcToBe instances to apply blocked assignments"""
    for rfc in RfcToBe.objects.filter(disposition_id="in_progress"):
        apply_blocked_assignment_for_rfc(rfc)


@with_rpcapi
def _compute_deep_references(
    related_doc_id: int,
    *,
    rpcapi: rpcapi_client.PurpleApi,
) -> None:
    """Compute 2nd and 3rd generation not-received references for an RfcToBe.

    Given an existing RpcRelatedDocument (not-received or refqueue), fetches
    the target's references from the Datatracker and creates not-received-2g
    relationships for each, then fetches each 2nd-gen reference's references
    and creates not-received-3g relationships.

    Duplicates are avoided by checking for existing relationships before creating
    new ones.
    """
    related_doc = RpcRelatedDocument.objects.select_related(
        "source",
        "target_document",
        "target_rfctobe__draft",
    ).get(pk=related_doc_id)
    source = related_doc.source

    if related_doc.target_document is not None:
        target_datatracker_id = related_doc.target_document.datatracker_id
    elif (
        related_doc.target_rfctobe is not None
        and related_doc.target_rfctobe.draft is not None
    ):
        target_datatracker_id = related_doc.target_rfctobe.draft.datatracker_id
    else:
        logger.warning("RpcRelatedDocument %d has no resolvable target", related_doc_id)
        return

    if target_datatracker_id is None:
        logger.warning(
            "RpcRelatedDocument %d target has no datatracker_id", related_doc_id
        )
        return

    # Collect datatracker IDs already linked to this source to avoid duplicates
    existing_target_dt_ids: set[int] = set(
        RpcRelatedDocument.objects.filter(
            source=source,
            relationship__slug__in=DocRelationshipName.REFERENCE_RELATIONSHIP_SLUGS,
            target_document__isnull=False,
        ).values_list("target_document__datatracker_id", flat=True)
    )

    # Datatracker IDs of drafts that already have an active RfcToBe
    active_rfctobe_dt_ids: set[int] = set(
        RfcToBe.objects.exclude(disposition_id="withdrawn")
        .filter(draft__datatracker_id__isnull=False)
        .values_list("draft__datatracker_id", flat=True)
    )

    refs_2g = rpcapi.get_draft_references(target_datatracker_id) or []
    for ref_2g in refs_2g:
        if ref_2g.id in active_rfctobe_dt_ids or ref_2g.id in existing_target_dt_ids:
            continue

        draft_2g = Document.objects.filter(
            datatracker_id=ref_2g.id
        ).first() or get_or_create_draft_by_name(ref_2g.name, rpcapi=rpcapi)
        if draft_2g is None:
            logger.warning(
                "Could not get or create document for 2G reference %s (id=%d)",
                ref_2g.name,
                ref_2g.id,
            )
            continue

        RpcRelatedDocument.objects.get_or_create(
            source=source,
            relationship=DocRelationshipName.NOT_RECEIVED_2G_RELATIONSHIP_SLUG,
            target_document=draft_2g,
        )
        existing_target_dt_ids.add(ref_2g.id)

        refs_3g = rpcapi.get_draft_references(ref_2g.id) or []
        for ref_3g in refs_3g:
            if (
                ref_3g.id in active_rfctobe_dt_ids
                or ref_3g.id in existing_target_dt_ids
            ):
                continue

            draft_3g = Document.objects.filter(
                datatracker_id=ref_3g.id
            ).first() or get_or_create_draft_by_name(ref_3g.name, rpcapi=rpcapi)
            if draft_3g is None:
                logger.warning(
                    "Could not get or create document for 3G reference %s (id=%d)",
                    ref_3g.name,
                    ref_3g.id,
                )
                continue

            RpcRelatedDocument.objects.get_or_create(
                source=source,
                relationship=DocRelationshipName.NOT_RECEIVED_3G_RELATIONSHIP_SLUG,
                target_document=draft_3g,
            )
            existing_target_dt_ids.add(ref_3g.id)


@shared_task
def compute_deep_references_task(related_doc_id: int):
    """Celery task to asynchronously compute 2G and 3G not-received references."""
    try:
        _compute_deep_references(related_doc_id)
    except Exception as e:
        logger.error(
            "Error computing deep references for RpcRelatedDocument %d: %s",
            related_doc_id,
            str(e),
        )
