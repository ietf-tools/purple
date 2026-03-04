# Copyright The IETF Trust 2025-2026, All Rights Reserved
"""RFC publication support

This module is for rpc app logic related to the publish_rfc API that the front-end
calls. Note that there is a similarly named module in the datatracker app
(datatracker.utils.publication) that contains logic for making the publish API call
to datatracker.
"""

import json
import logging
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory

import rpcapi_client
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rpcapi_client import ApiException

from datatracker.rpcapi import with_rpcapi
from datatracker.utils.publication import publish_rfc_metadata, upload_rfc_contents
from rpcauth.models import User

from ..models import RfcToBe
from .repo import GithubRepository, RepositoryError, TemporaryRepositoryError

logger = logging.getLogger(__name__)


def can_publish(rfctobe: RfcToBe, user: User):
    """Can this user publish this RfcToBe?

    Does not evaluate whether the RfcToBe is ready to be published.
    """
    if user.is_superuser:
        return True
    rpcperson = user.rpcperson()
    if rpcperson is None:
        return False
    return (
        rpcperson.assignment_set.active()
        .filter(
            rfc_to_be=rfctobe,
            role__slug="publisher",
        )
        .exists()
    )


def validate_ready_to_publish(rfctobe: RfcToBe):
    """Is this RfcToBe ready to be published?

    No return value. Raises serializers.ValidationError if not ready.

    detail messages should complete the sentence, "Cannot publish because..."
    """
    if rfctobe.disposition_id != "in_progress":
        raise serializers.ValidationError(
            f"disposition is '{rfctobe.disposition}, not 'In Progress'",
            code="rfctobe-bad-disposition",
        )
    if rfctobe.assignment_set.active().exclude(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document has open assignments other than publisher",
            code="rfctobe-open-assignments",
        )
    if not rfctobe.assignment_set.active().filter(role_id="publisher").exists():
        raise serializers.ValidationError(
            "document is not assigned a publisher",
            code="rfctobe-no-publisher",
        )
    if rfctobe.finalapproval_set.count() == 0:
        raise serializers.ValidationError(
            "no final approvals have been completed",
            code="rfctobe-no-final-approvals",
        )
    if rfctobe.finalapproval_set.active().exists():
        raise serializers.ValidationError(
            "final approvals are pending",
            code="rfctobe-pending-final-approvals",
        )
    if rfctobe.rfc_number is None:
        raise serializers.ValidationError(
            "no RFC number is assigned",
            code="rfctobe-no-rfc-number",
        )
    if rfctobe.repository.strip() == "":
        raise serializers.ValidationError("no repository is configured")
    # todo IANA check, what else?


def choose_files(publication_list):
    required_types = ["xml", "txt", "html", "pdf", "notprepped"]
    chosen = {type_: [] for type_ in required_types}

    for fileinfo in publication_list:
        type_ = fileinfo["type"]
        if type_ in chosen:
            chosen[type_].append(fileinfo["path"])
    missing = [type_ for type_ in chosen if len(chosen[type_]) == 0]
    if len(missing) > 0:
        raise MissingFilesError(f"Missing files: {', '.join(missing)}")
    multiples = [type_ for type_ in chosen if len(chosen[type_]) > 1]
    if len(multiples) > 0:
        raise AmbiguousFilesError(f"More than one of: {', '.join(multiples)}")
    return {k: v[0] for k, v in chosen.items()}


def suffix_for_type(type_):
    if type_ == "notprepped":
        return ".notprepped.xml"
    return "." + type_


_FORMAT_TYPE_TO_LABEL = {
    "xml": "XML",
    "txt": "TEXT",
    "html": "HTML",
    "pdf": "PDF",
}


def create_rfc_index_json(rfctobe: RfcToBe, chosen_files: dict, tmpdir: Path) -> Path:
    """Create an RFC index JSON file in tmpdir and return its path.
    """

    def _rfc_list(queryset) -> list[str]:
        """Convert a queryset of RfcToBe to a list of 'RFCNNNN' strings."""
        return [
            f"RFC{n}"
            for n in queryset.values_list("rfc_number", flat=True)
            if n is not None
        ]

    rfc_number = rfctobe.rfc_number
    doc_id = f"RFC{rfc_number}"

    authors = []
    for author in rfctobe.authors.all():
        name = author.titlepage_name
        if author.is_editor:
            name = f"{name}, Ed."
        authors.append(name)

    formats = [
        _FORMAT_TYPE_TO_LABEL[t]
        for t in _FORMAT_TYPE_TO_LABEL
        if t in chosen_files
    ]

    std_level = rfctobe.publication_std_level or rfctobe.std_level
    pub_status = std_level.name.upper() if std_level else ""

    stream = rfctobe.publication_stream or rfctobe.stream

    keywords_raw = rfctobe.keywords.strip() if rfctobe.keywords else ""
    keywords = (
        [k.strip() for k in keywords_raw.split(",") if k.strip()]
        if keywords_raw
        else []
    )

    pub_date = None
    if rfctobe.published_at:
        # April 1st RFCs get day prepended: "1 April YYYY"
        if rfctobe.is_april_first_rfc:
            pub_date = rfctobe.published_at.strftime("1 %B %Y")
        else:
            pub_date = rfctobe.published_at.strftime("%B %Y")

    data = {
        "draft": rfctobe.draft.name if rfctobe.draft else None,
        "doc_id": doc_id,
        "title": rfctobe.title,
        "authors": authors,
        "format": formats,
        "page_count": str(rfctobe.pages) if rfctobe.pages is not None else "",
        "pub_status": pub_status,
        "status": pub_status,
        "source": rfctobe.group or (stream.slug if stream else ""),
        "abstract": rfctobe.abstract,
        "pub_date": pub_date,
        "keywords": keywords,
        "obsoletes": _rfc_list(rfctobe.obsoletes),
        "obsoleted_by": _rfc_list(rfctobe.obsoleted_by),
        "updates": _rfc_list(rfctobe.updates),
        "updated_by": _rfc_list(rfctobe.updated_by),
        "see_also": [],
        "doi": f"10.17487/{doc_id}",
        "errata_url": None,
    }

    json_path = tmpdir / f"rfc{rfc_number}.json"
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.debug("Created RFC index JSON at %s", json_path)
    return json_path

@with_rpcapi
def publish_rfctobe(
    rfctobe: RfcToBe, expected_head: str, *, rpcapi: rpcapi_client.PurpleApi
):
    # Re-validate that the RfcToBe is ready to publish, things may have changed
    # since the task was queued.
    try:
        validate_ready_to_publish(rfctobe)
    except serializers.ValidationError as err:
        raise PublicationError(f"Cannot publish because {err}") from err

    repo = GithubRepository(rfctobe.repository)
    # Check that head commit matches expected_head. This check defines the instant
    # after which commits to the repository will be ignored for this publication
    # attempt.
    if repo.ref != expected_head:
        raise PublicationError(
            f"Cannot publish because HEAD of {rfctobe.repository} repo moved "
            f"(expected {expected_head}, found {repo.ref})"
        )

    # Call this the publication instant; actual save happens below, after datatracker
    # accepts the metadata update
    rfctobe.published_at = timezone.now()
    rfctobe.publication_std_level = rfctobe.std_level
    rfctobe.publication_stream = rfctobe.stream

    try:
        manifest = repo.get_manifest()
    except TemporaryRepositoryError as err:
        raise TemporaryPublicationError("Error retrieving manifest") from err
    except RepositoryError as err:
        raise PublicationError("Invalid or missing manifest") from err
    publications = manifest["publications"]
    for publication in publications:
        if rfctobe.rfc_number == publication["rfcNumber"]:
            break  # use this publication
    else:
        raise PublicationError(f"Manifest does not contain RFC {rfctobe.rfc_number}")
    # Choose files + validate that we have what we need / no ambiguities
    chosen_files = choose_files(publication["files"])
    downloaded_files = {}
    # Download the selected files to a temp directory
    with TemporaryDirectory(delete=not settings.DEBUG) as tmpdirname:
        logger.debug("Working in temp directory: %s", tmpdirname)
        output_stem = Path(tmpdirname) / f"rfc{rfctobe.rfc_number}"
        for type_, repo_path in chosen_files.items():
            output_path = output_stem.with_suffix(suffix_for_type(type_))
            logger.debug("Fetching %s", repo_path)
            repo_file = repo.get_file(repo_path)
            logger.debug("Saving as %s", str(output_path))
            try:
                with output_path.open("wb") as f:
                    for chunk in repo_file.chunks():
                        f.write(chunk)
            except TemporaryRepositoryError as err:
                raise TemporaryPublicationError from err
            downloaded_files[type_] = output_path

        # Now publish!
        logger.debug("Calling publish_rfc_metadata")
        try:
            publish_rfc_metadata(rfctobe, rpcapi=rpcapi)
        except rpcapi_client.exceptions.ServiceException as err:
            # a 5xx exception is probably a temporary datatracker server issue
            raise TemporaryPublicationError(str(err)) from err
        except ApiException as api_error:
            try:
                data = json.loads(api_error.body)
            except JSONDecodeError:
                raise PublicationError("unable to parse error body") from api_error
            # Sort out what's going on via error code
            error_codes = {err["code"] for err in data.get("errors", [])}
            if "invalid-draft" in error_codes:
                raise InvalidDraftError from api_error
            elif "already-published-draft" in error_codes:
                raise AlreadyPublishedDraftError from api_error
            else:
                raise PublicationError(
                    f"Publication failed: codes={error_codes}"
                ) from api_error
        # Datatracker accepted it, so mark the RfcToBe as published. N.b., we set
        # the published_at timestamp and other publication fields earlier.
        rfctobe.disposition_id = "published"
        rfctobe.save()

        # create the RFC index JSON file and upload all the files to datatracker.
        json_path = create_rfc_index_json(
            rfctobe, chosen_files, Path(tmpdirname)
        )

        try:
            upload_rfc_contents(
                rfctobe,
                filenames=[str(fn) for fn in downloaded_files.values()]
                + [str(json_path)],
                mtime=rfctobe.published_at,
                rpcapi=rpcapi,
            )
        except Exception as err:
            # The RFC was already published, but the files were not accepted.
            # This situation requires manual intervention until we make the
            # publication notification idempotent.
            raise PublicationError(
                f"Successfully notified datatracker that RFC {rfctobe.rfc_number} "
                f"was published, but uploading its files failed. Manual correction "
                f"is required."
            ) from err


class PublicationError(Exception):
    """Base class for publication exceptions"""


class TemporaryPublicationError(PublicationError):
    """Publication exception that is likely temporary and worth retrying"""


class AlreadyPublishedDraftError(PublicationError):
    """already-published-draft"""


class InvalidDraftError(PublicationError):
    """invalid-draft"""


class MissingFilesError(PublicationError):
    """Could not find all files to upload"""


class AmbiguousFilesError(PublicationError):
    """Unable to identify the files to upload"""
