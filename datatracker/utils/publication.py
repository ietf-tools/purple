# Copyright The IETF Trust 2025-2026, All Rights Reserved
"""Datatracker RFC publication

This module is for logic involved with notifying datatracker that an RFC has been
published and uploading the file contents. Note that there is a similarly named module
in the rpc app (rpc.lifecycle.publication) that contains logic related to the API the
purple front-end uses to trigger RFC publication.
"""

import datetime
import logging

import rpcapi_client
from rpcapi_client import RfcAuthorRequest, RfcPubRequest

from datatracker.rpcapi import with_rpcapi
from rpc.models import RfcToBe

logger = logging.getLogger(__name__)


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
                country="",  # purple does not model country
            )
            for author in rfctobe.authors.all()
        ],
        group=rfctobe.group,
        stream=rfctobe.publication_stream.slug,
        abstract=rfctobe.abstract,
        pages=rfctobe.pages,
        std_level=rfctobe.publication_std_level.slug,
        ad=(
            rfctobe.iesg_contact.datatracker_id
            if rfctobe.publication_stream_id == "ietf"
            else None
        ),
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
    mtime: datetime.datetime | None,
    *,
    rpcapi: rpcapi_client.PurpleApi,
):
    # set up and call API
    rpcapi.upload_rfc_files(
        rfc=rfctobe.rfc_number,
        mtime=mtime,
        contents=filenames,
    )
