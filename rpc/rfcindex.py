# Copyright The IETF Trust 2026, All Rights Reserved
from itertools import chain
from operator import attrgetter
from textwrap import fill

from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

from .models import RfcToBe, UnusableRfcNumber

logger = get_task_logger(__name__)


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

            # formats
            FORMATS_FOR_INDEX = ["txt", "html", "pdf", "xml", "ps"]
            formats = ", ".join(
                rfc.published_formats.filter(slug__in=FORMATS_FOR_INDEX).values_list(
                    "slug", flat=True
                )
            ).upper()

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


def createRfcTxtIndex():
    """
    Create index of published documents
    """
    DATE_FMT = "%m/%d/%Y"
    created_on = timezone.now().strftime(DATE_FMT)
    logger.info("Creating rfc-index.txt")
    index = render_to_string(
        "rpc/index/rfc-index.txt",
        {
            "created_on": created_on,
            "rfcs": get_rfc_text_index_entries(),
        },
    )
    print(index)  # TODO: Write to a blob store
    logger.info("Created rfc-index.txt")
