# Copyright The IETF Trust 2025, All Rights Reserved

from datetime import UTC, datetime
from uuid import uuid4
from xml.etree import ElementTree

from django.conf import settings

from rpc.models import RfcToBe

DATETIME_FMT = "%Y%m%d%H%M%S"


def _get_name_parts(name):
    """Return first name, last name and suffix"""
    # This is based on name split logic
    # https://github.com/rfc-editor/rpcwebsite/blob/master/rfc-ed/bin/rfc2doi.py

    first_name = ""
    last_name = ""
    suffix = ""

    if " " in name:
        (first_name, last_name) = name.split(" ", 1)
        if " " in last_name:
            (_last_name, suffix) = last_name.split(" ", 1)
            if len(suffix) < 4:  # Eastlake 3rd
                last_name = _last_name
            else:  # van Brandenburg
                suffix = ""
    else:
        last_name = name

    return (first_name, last_name, suffix)


def _get_contributors(author, sequence):
    """Return person_name or organization elements for author"""
    # collapse spaces
    name = [n for n in author.titlepage_name.split(" ") if len(n) > 0]
    role = "editor" if author.is_editor else "author"

    if name not in settings.AUTHOR_ORGS:
        # person_name
        (first_name, last_name, suffix) = _get_name_parts(name)
        person_name = ElementTree.Element(
            "person_name", sequence=sequence, contributor_role=role
        )
        if first_name:
            # person_name → first_name
            ElementTree.SubElement(person_name, "given_name").text = first_name
        if last_name:
            # person_name → surname
            ElementTree.SubElement(person_name, "surname").text = last_name
        if suffix:
            # person_name → suffix
            ElementTree.SubElement(person_name, "suffix").text = suffix
        return person_name
    else:
        # organization
        return ElementTree.Element(
            "organization", sequence=sequence, contributor_role=role
        )


def _generate_crossref_xml(rfc_number):
    """Generates a doi_batch XML with DOI data for crossref submission."""

    # get RFC data
    rfc = RfcToBe.objects.get(rfc_number=rfc_number)

    # construct XML
    root = ElementTree.Element(
        "doi_batch",
        attrib={
            "version": settings.CROSSREF_VERSION,
            "xmlns": f"http://www.crossref.org/schema/{settings.CROSSREF_VERSION}",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": f"http://www.crossref.org/schema/{settings.CROSSREF_VERSION} http://www.crossref.org/schema/deposit/crossref{settings.CROSSREF_VERSION}.xsd",
        },
    )

    # head
    head = ElementTree.SubElement(root, "head")
    ElementTree.SubElement(head, "doi_batch_id").text = str(uuid4())
    ElementTree.SubElement(head, "timestamp").text = datetime.now(UTC).strftime(
        DATETIME_FMT
    )

    # head → depositor
    depositor = ElementTree.SubElement(head, "depositor")
    ElementTree.SubElement(depositor, "depositor_name").text = settings.DOI_DEPOSITOR
    ElementTree.SubElement(depositor, "email_address").text = settings.DOI_EMAIL

    # head → registrant
    registrant = ElementTree.SubElement(head, "registrant")
    ElementTree.SubElement(registrant, "registrant_name").text = settings.DOI_REGISTRANT

    # body
    body = ElementTree.SubElement(root, "body")

    # body → report-paper
    report_paper = ElementTree.SubElement(body, "report-paper")
    report_paper.append(
        ElementTree.Comment(f"Translation of {rfc.doc_id} {rfc.stream}")
    )

    # body → report-paper → report-paper_metadata
    report_paper_metadata = ElementTree.SubElement(
        report_paper, "report-paper_metadata", language="en"
    )

    # body → report-paper → report-paper_metadata → contributors
    contributors = ElementTree.SubElement(report_paper_metadata, "contributors")
    sequence = "first"

    # body → report-paper → report-paper_metadata → contributors → person_name | organization
    for author in rfc.authors():
        contributors.append(_get_contributors(author, sequence))
        # change sequence
        if sequence == "first":
            sequence = "additional"

    # body → report-paper → report-paper_metadata → titles
    titles = ElementTree.SubElement(report_paper_metadata, "titles")

    # body → report-paper → report-paper_metadata → titles → title
    ElementTree.SubElement(titles, "title").text = rfc.title

    # body → report-paper → report-paper_metadata → publication_date
    pub_date = ElementTree.SubElement(
        report_paper_metadata, "publication_date", media_type="online"
    )

    # body → report-paper → report-paper_metadata → publication_date → month
    ElementTree.SubElement(pub_date, "month").text = rfc.published_at.month

    # body → report-paper → report-paper_metadata → publication_date → year
    ElementTree.SubElement(pub_date, "year").text = rfc.published_at.year

    # body → report-paper → report-paper_metadata → publisher
    publisher = ElementTree.SubElement(report_paper_metadata, "publisher")

    # body → report-paper → report-paper_metadata → publisher → publisher_name
    ElementTree.SubElement(publisher, "publisher_name").text = settings.DOI_REGISTRANT

    # body → report-paper → report-paper_metadata → publisher_item
    publisher_item = ElementTree.SubElement(report_paper_metadata, "publisher_item")

    # body → report-paper → report-paper_metadata → publisher_item → item_number
    ElementTree.SubElement(publisher_item, "item_number").text = rfc.doc_id.lower()

    # body → report-paper → report-paper_metadata → doi_data
    doi_data = ElementTree.SubElement(report_paper_metadata, "doi_data")

    # body → report-paper → report-paper_metadata → doi_data → doi
    ElementTree.SubElement(
        doi_data, "doi"
    ).text = f"{settings.DOI_PREFIX}/{rfc.doc_id.lower()}"

    # body → report-paper → report-paper_metadata → resource_data → resource
    ElementTree.SubElement(
        doi_data, "resource"
    ).text = f"{settings.DOI_URL}/{rfc.doc_id.lower()}"

    return root
