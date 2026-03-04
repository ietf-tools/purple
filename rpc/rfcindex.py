# Copyright The IETF Trust 2026, All Rights Reserved
from itertools import chain
from operator import attrgetter
from textwrap import fill
from xml.dom.minidom import parseString
from xml.etree import ElementTree

from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

from .models import RfcToBe, SubseriesMember, UnusableRfcNumber

logger = get_task_logger(__name__)
FORMATS_FOR_INDEX = ["txt", "html", "pdf", "xml", "ps"]


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

            # subseries
            subseries = ",".join(
                [
                    f"{s.type_id.upper()}{s.number:04d}"
                    for s in rfc.subseriesmember_set.all()
                ]
            )
            if subseries:
                subseries = f"(Also {subseries}) "

            entry = fill(
                (
                    f"{rfc.rfc_number:04d} {rfc.title}. {authors}. {date}. "
                    f"(Format: {formats}){doc_relations}{subseries}"
                    f"(Status: {str(rfc.std_level).upper()}) "
                    f"(DOI: {settings.DOI_PREFIX}/RFC{rfc.rfc_number:04d})"
                ),
                width=75,
                subsequent_indent=" " * 5,
            )
            entries.append(entry)

    return entries


def load_bcp_xml_index_entries(rfc_index):
    """Load BCP entries for rfc-index.xml"""
    entries = []

    highest_bcp_number = (
        SubseriesMember.objects.filter(type_id="bcp").order_by("-number").first().number
    )

    for bcp_number in range(1, highest_bcp_number):
        entry = ElementTree.SubElement(rfc_index, "bcp-entry")
        ElementTree.SubElement(entry, "doc-id").text = f"BCP{bcp_number:04d}"

        subseries_members = SubseriesMember.objects.filter(
            type_id="bcp", number=bcp_number
        )
        if subseries_members:
            is_also = ElementTree.SubElement(entry, "is-also")

            for bcp_entry in subseries_members:
                ElementTree.SubElement(
                    is_also, "doc-id"
                ).text = f"RFC{bcp_entry.rfc_to_be.rfc_number:04d}"

        entries.append(entry)


def load_fyi_xml_index_entries(rfc_index):
    """Returns FYI entries for rfc-index.xml"""
    entries = []

    published_fyis = (
        SubseriesMember.objects.filter(type_id="fyi").order_by("number").distinct()
    )

    for fyi in published_fyis:
        entry = ElementTree.SubElement(rfc_index, "fyi-entry")
        ElementTree.SubElement(entry, "doc-id").text = f"FYI{fyi.number:04d}"
        is_also = ElementTree.SubElement(entry, "is-also")

        for fyi_entry in SubseriesMember.objects.filter(
            type_id="fyi", number=fyi.number
        ):
            ElementTree.SubElement(
                is_also, "doc-id"
            ).text = f"RFC{fyi_entry.rfc_to_be.rfc_number:04d}"

        entries.append(entry)


def load_std_xml_index_entries(rfc_index):
    """Load std entries for rfc-index.xml"""
    entries = []

    published_stds = (
        SubseriesMember.objects.filter(type_id="std").order_by("number").distinct()
    )

    for std in published_stds:
        entry = ElementTree.SubElement(rfc_index, "std-entry")
        ElementTree.SubElement(entry, "doc-id").text = f"STD{std.number:04d}"
        is_also = ElementTree.SubElement(entry, "is-also")

        for std_entry in SubseriesMember.objects.filter(
            type_id="std", number=std.number
        ):
            ElementTree.SubElement(
                is_also, "doc-id"
            ).text = f"RFC{std_entry.rfc_to_be.rfc_number:04d}"

        entries.append(entry)


def load_rfc_not_be_xml_index_entries(rfc_index):
    """Load unusable RFC entries for rfc-index.xml"""
    entries = []

    for record in UnusableRfcNumber.objects.order_by("number"):
        entry = ElementTree.SubElement(rfc_index, "rfc-not-issued-entry")
        ElementTree.SubElement(entry, "doc-id").text = f"RFC{record.number:04d}"
        entries.append(entry)


def load_rfc_xml_index_entries(rfc_index):
    """Load RFC entries for rfc-index.xml"""
    entries = []

    published_rfcs = RfcToBe.objects.filter(published_at__isnull=False).order_by(
        "rfc_number"
    )
    for rfc in published_rfcs:
        entry = ElementTree.SubElement(rfc_index, "rfc-entry")

        ElementTree.SubElement(entry, "doc-id").text = f"RFC{rfc.rfc_number:04d}"
        ElementTree.SubElement(entry, "title").text = rfc.title

        for author in rfc.authors.all():
            author_element = ElementTree.SubElement(entry, "author")
            ElementTree.SubElement(author_element, "name").text = author.titlepage_name
            if author.is_editor:
                ElementTree.SubElement(author_element, "title").text = "Editor"

        date = ElementTree.SubElement(entry, "date")
        ElementTree.SubElement(date, "month").text = rfc.published_at.strftime("%B")
        if rfc.is_april_first_rfc:
            ElementTree.SubElement(date, "day").text = str(rfc.published_at.day)
        ElementTree.SubElement(date, "year").text = str(rfc.published_at.year)

        format = ElementTree.SubElement(entry, "format")
        for file_format in rfc.published_formats.filter(
            slug__in=FORMATS_FOR_INDEX
        ).values_list("slug", flat=True):
            ElementTree.SubElement(format, "file-format").text = file_format.upper()

        ElementTree.SubElement(entry, "page-count").text = str(rfc.pages)

        if rfc.obsoletes:
            obsoletes = ElementTree.SubElement(entry, "obsoletes")
            for rfc_number in rfc.obsoletes.values_list(
                "rfc_number", flat=True
            ).order_by("rfc_number"):
                ElementTree.SubElement(
                    obsoletes, "doc-id"
                ).text = f"RFC{rfc_number:04d}"

        if rfc.updates:
            updates = ElementTree.SubElement(entry, "updates")
            for rfc_number in rfc.updates.values_list("rfc_number", flat=True).order_by(
                "rfc_number"
            ):
                ElementTree.SubElement(updates, "doc-id").text = f"RFC{rfc_number:04d}"

        if rfc.obsoleted_by:
            obsoleted_by = ElementTree.SubElement(entry, "obsoleted-by")
            for rfc_number in rfc.obsoleted_by.values_list(
                "rfc_number", flat=True
            ).order_by("rfc_number"):
                ElementTree.SubElement(
                    obsoleted_by, "doc-id"
                ).text = f"RFC{rfc_number:04d}"

        if rfc.updated_by:
            updated_by = ElementTree.SubElement(entry, "updated-by")
            for rfc_number in rfc.updated_by.values_list(
                "rfc_number", flat=True
            ).order_by("rfc_number"):
                ElementTree.SubElement(
                    updated_by, "doc-id"
                ).text = f"RFC{rfc_number:04d}"

        if rfc.keywords.strip():
            keywords = ElementTree.SubElement(entry, "keywords")
            for keyword in rfc.keywords.strip().split(","):
                ElementTree.SubElement(keywords, "kw").text = keyword.strip()

        if rfc.abstract:
            abstract = ElementTree.SubElement(entry, "abstract")
            ElementTree.SubElement(abstract, "p").text = rfc.abstract

        if rfc.draft:
            ElementTree.SubElement(entry, "draft").text = str(rfc.draft)

        ElementTree.SubElement(entry, "current-status").text = str(
            rfc.std_level
        ).upper()
        ElementTree.SubElement(entry, "publication-status").text = str(
            rfc.publication_std_level
        ).upper()
        ElementTree.SubElement(entry, "stream").text = str(rfc.stream)
        ElementTree.SubElement(entry, "area").text = ""

        if rfc.group:
            ElementTree.SubElement(entry, "wg_acronym").text = str(rfc.group)

        ElementTree.SubElement(
            entry, "errata-url"
        ).text = f"{settings.ERRATA_URL}/rfc{rfc.rfc_number}"
        ElementTree.SubElement(
            entry, "doi"
        ).text = f"{settings.DOI_PREFIX}/RFC{rfc.rfc_number:04d}"
        entries.append(entry)


def createRfcTxtIndex():
    """
    Create text index of published documents
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


def createRfcXmlIndex():
    """
    Create XML index of published documents
    """
    logger.info("Creating rfc-index.xml")
    rfc_index = ElementTree.Element(
        "rfc-index",
        attrib={
            "xmlns": "https://www.rfc-editor.org/rfc-index",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": (
                "https://www.rfc-editor.org/rfc-index "
                "https://www.rfc-editor.org/rfc-index.xsd"
            ),
        },
    )

    # load data
    load_bcp_xml_index_entries(rfc_index)
    load_fyi_xml_index_entries(rfc_index)
    load_rfc_not_be_xml_index_entries(rfc_index)
    load_rfc_xml_index_entries(rfc_index)
    load_std_xml_index_entries(rfc_index)

    # make it pretty
    rough_index = parseString(ElementTree.tostring(rfc_index, encoding="UTF-8"))
    pretty_index = rough_index.toprettyxml(indent=" " * 4, encoding="UTF-8")
    print(pretty_index.decode())  # TODO: Write to a blob store
    logger.info("Created rfc-index.xml")
