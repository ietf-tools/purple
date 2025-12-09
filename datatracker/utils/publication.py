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


def choose_files(filenames):
    interesting_extensions = [".xml", ".txt", ".html", ".txt.pdf"]
    chosen = {ext: [] for ext in interesting_extensions}
    for fname in filenames:
        suffix = "".join(Path(fname).suffixes)
        if suffix in chosen:
            chosen[suffix].append(fname)
    missing = [ext for ext in chosen if len(chosen[ext]) == 0]
    if len(missing) > 0:
        raise MissingFilesError(
            f"Missing files: {", ".join(missing)}"
        )
    multiples = [ext for ext in chosen if len(chosen[ext]) > 1]
    if len(multiples) > 0:
        raise AmbiguousFilesError(
            f"More than one of: {", ".join(multiples)}"
        )
    return [v[0] for v in chosen.values()]


@with_rpcapi
def publish_rfc(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    # todo add guards
    #  - missing rfc_number
    #  - state of rfctobe
    #  - missing published_at
    # todo error handling
    if rfctobe.repository.strip() == "":
        raise PublicationError("Cannot publish without a repository")
    repo = GithubRepository(rfctobe.repository)
    # List the files in the directory
    logger.debug(f"Using files in {rfctobe.repository}/{rfctobe.repository_path}")
    try:
        repo_files = {
            Path(rf.name).name: rf
            for rf in repo.directory_contents(rfctobe.repository_path)
        }
    except RepositoryError as err:
        raise PublicationError from err
    # Select the files by name (may raise exceptions, let those bubble up)
    filenames = choose_files(repo_files.keys())
    logger.debug(f"Chose: {filenames}")
    # Download the selected files to a temp directory
    with TemporaryDirectory() as tmpdirname:
        tmppath = Path(tmpdirname)
        for fname in filenames:
            output_path = tmppath / fname
            logger.debug(f"Writing to {output_path}")
            with output_path.open("wb") as f:
                for chunk in repo_files[fname].chunks():
                    f.write(chunk)
        # Now publish!
        logger.debug("Calling publish_rfc_metad")
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
        upload_rfc_contents(rfctobe, filenames, rpcapi=rpcapi)


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
