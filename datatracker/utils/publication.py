# Copyright The IETF Trust 2025, All Rights Reserved
import datetime
import json
from json import JSONDecodeError

import rpcapi_client
from rpcapi_client import AuthorRequest, RfcPubRequest, ApiException

from datatracker.rpcapi import with_rpcapi


@with_rpcapi
def publish_rfc(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    # todo add guards
    #  - missing rfc_number
    #  - state of rfctobe
    # todo error handling
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
    upload_rfc_contents(rfctobe, rpcapi=rpcapi)


@with_rpcapi
def publish_rfc_metadata(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    rfc_pub_req = RfcPubRequest(
        published=datetime.datetime.now(tz=datetime.UTC),  # todo real pub date
        rfc_number=rfctobe.rfc_number,
        title=rfctobe.title,
        authors=[
            AuthorRequest(
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
def upload_rfc_contents(rfctobe, *, rpcapi: rpcapi_client.PurpleApi):
    """todo implement"""


class PublicationError(Exception):
    """Base class for publication exceptions"""


class AlreadyPublishedDraftError(PublicationError):
    """already-published-draft"""


class InvalidDraftError(PublicationError):
    """invalid-draft"""
