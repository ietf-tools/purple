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
    """
    if rfctobe.disposition_id != "in_progress":
        raise serializers.ValidationError(
            "disposition is not 'in_progress'",
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
    # todo IANA check, what else?


def choose_files(publication_list):
    required_types = ["xml", "txt", "html", "pdf", "json", "notprepped"]
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


@with_rpcapi
def publish_rfctobe(
    rfctobe: RfcToBe, expected_head: str, *, rpcapi: rpcapi_client.RpcApi
):
    if rfctobe.rfc_number is None:
        raise PublicationError("Cannot publish without an rfc_number")
    if rfctobe.repository.strip() == "":
        raise PublicationError("Cannot publish without a repository")
    if rfctobe.disposition_id != "in_progress":
        raise PublicationError(
            f"Cannot publish because disposition is {rfctobe.disposition_id}"
        )

    repo = GithubRepository(rfctobe.repository)
    # Check that head commit matches expected_head. This check defines the instant
    # after which commits to the repository will be ignored for this publication
    # attempt. Call this the publication instant.
    rfctobe.published_at = timezone.now()  # not yet saved!!
    if repo.ref != expected_head:
        raise PublicationError(
            f"Cannot publish because HEAD of {rfctobe.repository} repo moved "
            f"(expected {expected_head}, found {repo.ref})"
        )
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
    with TemporaryDirectory() as tmpdirname:
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

        # Datatracker accepted it, so mark the RfcToBe as published. N.b., we set
        # the published_at timestamp earlier.
        rfctobe.disposition_id = "published"
        rfctobe.publication_std_level = rfctobe.std_level
        rfctobe.publication_stream = rfctobe.stream
        rfctobe.save()

        try:
            upload_rfc_contents(
                rfctobe,
                filenames=[str(fn) for fn in downloaded_files.values()],
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
