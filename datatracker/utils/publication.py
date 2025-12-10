# Copyright The IETF Trust 2025, All Rights Reserved
"""Datatracker RFC publication

This module is for logic involved with notifying datatracker that an RFC has been
published and uploading the file contents. Note that there is a similarly named module
in the rpc app (rpc.lifecycle.publication) that contains logic related to the API the
purple front-end uses to trigger RFC publication.
"""

import json
import logging
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory

import rpcapi_client
from rpcapi_client import ApiException, RfcAuthorRequest, RfcPubRequest

from datatracker.rpcapi import with_rpcapi
from rpc.lifecycle.repo import GithubRepository, RepositoryError
from rpc.models import RfcToBe

logger = logging.getLogger(__name__)


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
def publish_rfc(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    # todo add guards
    #  - state of rfctobe
    #  - missing published_at
    # todo error handling
    if rfctobe.rfc_number is None:
        raise PublicationError("Cannot publish without an rfc_number")
    if rfctobe.repository.strip() == "":
        raise PublicationError("Cannot publish without a repository")
    repo = GithubRepository(rfctobe.repository)
    try:
        manifest = repo.get_manifest()
    except RepositoryError as err:
        raise PublicationError(
            "Invalid or missing manifest or retrieval error"
        ) from err
    publications = manifest["publications"]
    for publication in publications:
        if rfctobe.rfc_number == publication["rfcNumber"]:
            break  # use this publication
    else:
        raise PublicationError(f"Manifest does not contain RFC {rfctobe.rfc_number}")
    # Choose files + validate that we have what we need / no ambiguities
    chosen_files = choose_files(publication)
    downloaded_files = {}
    # Download the selected files to a temp directory
    with TemporaryDirectory() as tmpdirname:
        output_stem = Path(tmpdirname) / f"rfc{rfctobe.rfc_number}"
        for type_, repo_path in chosen_files:
            output_path = output_stem.with_suffix(suffix_for_type(type_))
            logger.debug("Fetching %s", repo_path)
            repo_file = repo.get_file(repo_path)
            logger.debug("Saving as %s", str(output_path))
            with output_path.open("wb") as f:
                for chunk in repo_file.chunks():
                    f.write(chunk)
            downloaded_files[type_] = output_path
        # Now publish!
        logger.debug("Calling publish_rfc_metadata")
        try:
            publish_rfc_metadata(rfctobe, rpcapi=rpcapi)
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
        upload_rfc_contents(
            rfctobe,
            [str(fn) for fn in downloaded_files.values()],
            rpcapi=rpcapi,
        )


@with_rpcapi
def publish_rfc_metadata(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    rfc_pub_req = RfcPubRequest(
        published=rfctobe.published_at,
        rfc_number=rfctobe.rfc_number,
        title=rfctobe.title,
        authors=[
            RfcAuthorRequest(
                titlepage_name=author.titlepage_name,
                is_editor=author.is_editor,
                person=(
                    author.datatracker_person.datatracker_id
                    if author.datatracker_person is not None
                    else None
                ),
                email=author.datatracker_person.email,
                affiliation=author.affiliation or "",
                country="",  # todo author country?
            )
            for author in rfctobe.authors.all()
        ],
        # group=<not implemented, comes from draft>
        stream=rfctobe.intended_stream.slug,
        # abstract="This is the abstract. It is not yet modeled.",
        # pages=None,  # todo pages
        # words=None,  # todo words
        # formal_languages=<not implemented, comes from draft>
        std_level=rfctobe.intended_std_level.slug,
        # ad=<not implemented, comes from draft>
        # note=<not implemented, comes from draft>
        obsoletes=list(
            rfctobe.obsoletes.exclude(
                # obsoleting an RFC that has no rfc_number is nonsensical, but
                # guard just in case
                rfc_number__isnull=True
            ).values_list("rfc_number", flat=True)
        ),
        updates=list(
            rfctobe.updates.exclude(
                # updating an RFC that has no rfc_number is nonsensical, but
                # guard just in case
                rfc_number__isnull=True
            ).values_list("rfc_number", flat=True)
        ),
        subseries=[
            f"{subseries.type.slug}{subseries.number}"
            for subseries in rfctobe.subseriesmember_set.all()
        ],
        # todo changes_status_of (needs datatracker support, too)
    )
    if rfctobe.draft is not None:
        rfc_pub_req.draft_name = rfctobe.draft.name
        rfc_pub_req.draft_rev = rfctobe.draft.rev
    rpcapi.notify_rfc_published(rfc_pub_req)


@with_rpcapi
def upload_rfc_contents(
    rfctobe: RfcToBe, filenames: list[str], *, rpcapi: rpcapi_client.PurpleApi
):
    # set up and call API
    rpcapi.upload_rfc_files(rfc=rfctobe.rfc_number, contents=filenames)


class PublicationError(Exception):
    """Base class for publication exceptions"""


class AlreadyPublishedDraftError(PublicationError):
    """already-published-draft"""


class InvalidDraftError(PublicationError):
    """invalid-draft"""


class MissingFilesError(PublicationError):
    """Could not find all files to upload"""


class AmbiguousFilesError(PublicationError):
    """Unable to identify the files to upload"""
