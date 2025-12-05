# Copyright The IETF Trust 2025, All Rights Reserved
"""Datatracker RFC publication

This module is for logic involved with notifying datatracker that an RFC has been
published and uploading the file contents. Note that there is a similarly named module
in the rpc app (rpc.lifecycle.publication) that contains logic related to the API the
purple front-end uses to trigger RFC publication.
"""

import json
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory

import rpcapi_client
from github import Github
from rpcapi_client import ApiException, RfcAuthorRequest, RfcPubRequest

from datatracker.rpcapi import with_rpcapi
from rpc.models import RfcToBe


@with_rpcapi
def publish_rfc(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    # todo add guards
    #  - missing rfc_number
    #  - state of rfctobe
    #  - missing published_at
    # todo error handling
    if rfctobe.repository.strip() == "":
        raise PublicationError("Cannot publish without a repository")
    # First pass at reading files from GH. Needs error handling / validation
    #  - decide how files are actually identified
    #  - expected files present
    #  - dealing with missing files
    #  - (maybe) dealing with filename conflicts (if file ID is suffix-based)
    #  - be more careful about file paths (repo_file.name might have directories in it)
    gh = Github()
    repo = gh.get_repo(rfctobe.repository)
    repo_contents = repo.get_contents(rfctobe.repository_path)
    interesting_extensions = [".xml", ".txt", ".html", ".txt.pdf"]
    filenames = []
    with TemporaryDirectory() as tmpdirname:
        # populate it with files from GH repo
        tmppath = Path(tmpdirname)
        for repo_file in repo_contents:
            if repo_file.type == "dir":
                continue
            repo_file_suffix = "".join(Path(repo_file.name).suffixes)
            if repo_file_suffix not in interesting_extensions:
                continue
            output_path = tmppath / repo_file.name
            with output_path.open("wb") as f:
                f.write(repo_file.decoded_content)
            filenames.append(str(output_path))
        # validate those against what was queued with the task (?)

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
    rfctobe: RfcToBe,
    filenames: list[str],
    *,
    rpcapi: rpcapi_client.PurpleApi
):
    # set up and call API
    rpcapi.upload_rfc_files(rfc=rfctobe.rfc_number, contents=filenames)


class PublicationError(Exception):
    """Base class for publication exceptions"""


class AlreadyPublishedDraftError(PublicationError):
    """already-published-draft"""


class InvalidDraftError(PublicationError):
    """invalid-draft"""
