# Copyright The IETF Trust 2026, All Rights Reserved
from celery import shared_task
from celery.utils.log import get_task_logger

from ..lifecycle.metadata import Metadata
from ..lifecycle.repo import GithubRepository
from ..models import MetadataValidationResults, RfcToBe

logger = get_task_logger(__name__)


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
