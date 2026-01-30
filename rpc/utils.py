# Copyright The IETF Trust 2023-2024, All Rights Reserved
from itertools import chain
from operator import attrgetter
from textwrap import fill

from django.conf import settings
from django.db.models import F, Max

from datatracker.models import Document

from .models import DumpInfo, RfcToBe, UnusableRfcNumber
from .serializers import CreateRpcRelatedDocumentSerializer


class VersionInfo:
    """Application version information model"""

    version = "version-access-not-yet-implemented"

    def __init__(self):
        # If we have a DumpInfo, populate the dump_timestamp property
        dumpinfo = DumpInfo.objects.order_by("-timestamp").first()
        if dumpinfo is not None:
            self.dump_timestamp = dumpinfo.timestamp


def next_rfc_number(count=1) -> list[int]:
    """Find the next count contiguous available RFC numbers"""
    # In the worst-case, we can always use (n + 1) to (n + count) where n is the last
    # unavailable number.
    last_unavailable_number = max(
        (
            UnusableRfcNumber.objects.aggregate(Max("number"))["number__max"] or 0,
            RfcToBe.objects.aggregate(Max("rfc_number"))["rfc_number__max"] or 0,
            # todo get last RFC number from datatracker
        )
    )
    # todo consider holes in the unavailable number sequence
    return list(range(last_unavailable_number + 1, last_unavailable_number + 1 + count))


def create_rpc_related_document(relationship_slug, source, target_draft_name):
    data = {
        "relationship": relationship_slug,
        "source": source,
        "target_draft_name": target_draft_name,
    }

    serializer = CreateRpcRelatedDocumentSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        return serializer.save()
    return None


def get_or_create_draft_by_name(draft_name, *, rpcapi):
    """Get a datatracker Document for a draft given its name

    n.b., creates a Document object if needed
    """
    drafts = rpcapi.get_drafts_by_names([draft_name])

    draft_info = next(
        (d for d in drafts if getattr(d, "name", None) == draft_name), None
    )
    if draft_info is None:
        return None
    # todo manage updates if the details below change before draft reaches pubreq!
    document, _ = Document.objects.get_or_create(
        datatracker_id=draft_info.id,
        defaults={
            "name": draft_info.name,
            "rev": draft_info.rev,
            "title": draft_info.title,
            "stream": "" if draft_info.stream is None else draft_info.stream,
            "pages": draft_info.pages,
            "intended_std_level": getattr(draft_info, "intended_std_level", "") or "",
        },
    )
    return document


def get_rfc_text_index_entries():
    """Returns RFC entries for rfc-index.txt"""
    entries = []

    published_rfcs = RfcToBe.objects.filter(published_at__isnull=False).order_by(
        "rfc_number"
    )
    unususable = UnusableRfcNumber.objects.annotate(rfc_number=F("number")).all()
    rfcs = sorted(chain(published_rfcs, unususable), key=attrgetter("rfc_number"))
    for rfc in rfcs:
        if isinstance(rfc, UnusableRfcNumber):
            entries.append(f"{rfc.rfc_number:04d} Not Issued.")
        else:
            authors = ", ".join(rfc.authors.values_list("titlepage_name", flat=True))
            date = (
                rfc.published_at.strftime("1 %B %Y")
                if rfc.is_april_first_rfc
                else rfc.published_at.strftime("%B %Y")
            )

            formats = ", ".join(["TXT", "HTML"])  # TODO: Populate formats

            # obsoletes
            obsoletes = ""
            if rfc.obsoletes:
                obsoleting_rfcs = ", ".join(
                    f"RFC{rfc_number:04d}"
                    for rfc_number in rfc.obsoletes.values_list(
                        "rfc_number", flat=True
                    ).order_by("rfc_number")
                )
                obsoletes = f" (Obsoletes {obsoleting_rfcs})"

            # obsoleted by
            obsoleted_by = ""
            if rfc.obsoleted_by:
                obsoleting_rfcs = ", ".join(
                    f"RFC{rfc_number:04d}"
                    for rfc_number in rfc.obsoleted_by.values_list(
                        "rfc_number", flat=True
                    ).order_by("rfc_number")
                )
                obsoleted_by = f" (Obsoleted by {obsoleting_rfcs})"

            # updates
            updates = ""
            if rfc.updates:
                updating_rfcs = ", ".join(
                    f"RFC{rfc_number:04d}"
                    for rfc_number in rfc.updates.values_list(
                        "rfc_number", flat=True
                    ).order_by("rfc_number")
                )
                updates = f" (Updates {updating_rfcs})"

            # updated by
            updated_by = ""
            if rfc.updated_by:
                updating_rfcs = ", ".join(
                    f"RFC{rfc_number:04d}"
                    for rfc_number in rfc.updated_by.values_list(
                        "rfc_number", flat=True
                    ).order_by("rfc_number")
                )
                updated_by = f" (Updated by {updating_rfcs})"

            doc_relations = f"{obsoletes}{obsoleted_by}{updates}{updated_by} "

            entry = fill(
                (
                    f"{rfc.rfc_number:04d} {rfc.title}. {authors}. {date}. "
                    f"(Format: {formats}){doc_relations}"
                    f"(Status: {str(rfc.publication_std_level).upper()}) "
                    f"(DOI: {settings.DOI_PREFIX}/RFC{rfc.rfc_number:04d})"
                ),
                width=75,
                subsequent_indent=" " * 5,
            )
            entries.append(entry)

    return entries
