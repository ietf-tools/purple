# Copyright The IETF Trust 2025-2026, All Rights Reserved
import rpcapi_client
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import F
from django.utils import timezone

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
from .rfcindex import mark_rfcindex_as_processed, refresh_rfc_index, rfcindex_is_dirty
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
    if rfcindex_is_dirty():
        logger.info("RFC index data has updates, refreshing")
        new_processed_time = timezone.now()
        refresh_rfc_index()
        mark_rfcindex_as_processed(new_processed_time)
    else:
        logger.debug("RFC index not updated, skipping")


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
    """Recompute all 2G and 3G not-received references for an RfcToBe source.

    Called when a 1G (not-received or refqueue) relationship is created or
    updated.  Deletes all existing auto-computed 2G/3G relationships for the
    source and rebuilds them from scratch.
    """
    related_doc = RpcRelatedDocument.objects.select_related("source").get(
        pk=related_doc_id
    )
    source = related_doc.source

    # Delete all previously auto-computed 2G/3G relations — rebuild from scratch.
    RpcRelatedDocument.objects.filter(
        source=source,
        relationship__slug__in=[
            DocRelationshipName.NOT_RECEIVED_2G_RELATIONSHIP_SLUG,
            DocRelationshipName.NOT_RECEIVED_3G_RELATIONSHIP_SLUG,
        ],
    ).delete()

    # Fetch all current 1G relations for this source.
    refs_1g = list(
        RpcRelatedDocument.objects.filter(
            source=source,
            relationship__slug__in=[
                DocRelationshipName.NOT_RECEIVED_RELATIONSHIP_SLUG,
                DocRelationshipName.REFQUEUE_RELATIONSHIP_SLUG,
            ],
        ).select_related("target_document", "target_rfctobe__draft")
    )

    # IDs of drafts that already have an active RfcToBe
    received_dt_ids_list: set[int] = set(
        RfcToBe.objects.exclude(disposition_id="withdrawn")
        .filter(draft__datatracker_id__isnull=False)
        .values_list("draft__datatracker_id", flat=True)
    )

    # Seed received_dt_ids with all 1G target IDs so they are not re-added as 2G/3G.
    received_dt_ids: set[int] = set(received_dt_ids_list)
    for ref in refs_1g:
        if (
            ref.target_document is not None
            and ref.target_document.datatracker_id is not None
        ):
            received_dt_ids.add(ref.target_document.datatracker_id)
        elif (
            ref.target_rfctobe is not None
            and ref.target_rfctobe.draft is not None
            and ref.target_rfctobe.draft.datatracker_id is not None
        ):
            received_dt_ids.add(ref.target_rfctobe.draft.datatracker_id)

    for ref in refs_1g:
        if ref.target_document is not None:
            target_dt_id = ref.target_document.datatracker_id
        elif ref.target_rfctobe is not None and ref.target_rfctobe.draft is not None:
            target_dt_id = ref.target_rfctobe.draft.datatracker_id
        else:
            logger.warning("1G RpcRelatedDocument %d has no resolvable target", ref.pk)
            continue

        if target_dt_id is None:
            logger.warning(
                "1G RpcRelatedDocument %d target has no datatracker_id", ref.pk
            )
            continue

        refs_2g = rpcapi.get_draft_references(target_dt_id) or []
        created_2g_ids: list[int] = []

        for ref_2g in refs_2g:
            # prevent duplicate processing of same 2G
            if ref_2g.id in received_dt_ids:
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
            received_dt_ids.add(ref_2g.id)
            created_2g_ids.append(ref_2g.id)

        for ref_2g_id in created_2g_ids:
            refs_3g = rpcapi.get_draft_references(ref_2g_id) or []
            for ref_3g in refs_3g:
                if ref_3g.id in received_dt_ids:
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
                received_dt_ids.add(ref_3g.id)


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
