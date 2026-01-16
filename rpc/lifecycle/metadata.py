# Copyright The IETF Trust 2026, All Rights Reserved
"""Document metadata interfaces"""

import datetime
import logging
import xml.etree.ElementTree as ET
from itertools import zip_longest

from django.db import transaction

from rpc.models import (
    DocRelationshipName,
    RfcToBe,
    RpcRelatedDocument,
    SubseriesMember,
    SubseriesTypeName,
)

logger = logging.getLogger(__name__)


class Metadata:
    """Base class for metadata extraction"""

    @staticmethod
    def parse_rfc_xml(xml_string):
        root = ET.fromstring(xml_string)
        ns = {}

        front = root.find("front", ns)
        if front is None:
            return None

        title_elem = front.find("title", ns)
        title = title_elem.text.strip() if title_elem is not None else ""

        abstract_elem = front.find("abstract", ns)
        abstract_text = ""
        if abstract_elem is not None:
            abstract_text = " ".join(
                t.text.strip() for t in abstract_elem.findall("t", ns) if t.text
            )

        authors = []
        for author in front.findall("author", ns):
            author_dict = dict(author.attrib)
            org_elem = author.find("organization", ns)
            if org_elem is not None and org_elem.text:
                author_dict["organization"] = org_elem.text.strip()
            if author_dict:
                authors.append(author_dict)

        obsoletes_str = root.attrib.get("obsoletes", "")
        obsoletes = (
            [s.strip() for s in obsoletes_str.split(",") if s.strip()]
            if obsoletes_str
            else []
        )

        updates_str = root.attrib.get("updates", "")
        updates = (
            [s.strip() for s in updates_str.split(",") if s.strip()]
            if updates_str
            else []
        )

        date_elem = front.find("date", ns)
        date = None
        if date_elem is not None:
            date = {
                "month": date_elem.attrib.get("month"),
                "day": date_elem.attrib.get("day"),
                "year": date_elem.attrib.get("year"),
            }

        subseries = []
        for series_info in root.findall("seriesInfo", ns):
            name = series_info.attrib.get("name")
            if name in ("BCP", "FYI", "STD"):
                value = series_info.attrib.get("value")
                if name and value:
                    subseries.append({"name": name, "value": value})

        return {
            "title": title,
            "abstract": abstract_text,
            "authors": authors,
            "obsoletes": obsoletes,
            "updates": updates,
            "publication_date": date,
            "subseries": subseries,
        }

    @staticmethod
    def update_metadata(rfctobe, metadata):
        """Update the draft title from metadata dictionary"""

        updated_fields = {}

        with transaction.atomic():
            # title
            new_title = metadata.get("title")
            draft = rfctobe.draft
            if not new_title:
                raise ValueError("No title in metadata")
            draft.title = new_title
            draft.save(update_fields=["title"])
            updated_fields["title"] = new_title

            # obsoletes and updates
            # Delete existing obsoletes and updates relationships
            RpcRelatedDocument.objects.filter(
                source=rfctobe, relationship__slug__in=["obs", "updates"]
            ).delete()

            # Create new obsoletes relationships
            obsoletes = metadata.get("obsoletes", [])
            relationship = DocRelationshipName.objects.get(slug="obs")
            for rfc_num in obsoletes:
                try:
                    target_rfctobe = RfcToBe.objects.get(rfc_number=rfc_num)
                    RpcRelatedDocument.objects.create(
                        source=rfctobe,
                        relationship=relationship,
                        target_rfctobe=target_rfctobe,
                    )
                except RfcToBe.DoesNotExist:
                    logger.warning(
                        f"RFC {rfc_num} not found for obsoletes relationship"
                    )

            # Create new updates relationships
            updates = metadata.get("updates", [])
            relationship = DocRelationshipName.objects.get(slug="updates")
            for rfc_num in updates:
                try:
                    target_rfctobe = RfcToBe.objects.get(rfc_number=rfc_num)
                    RpcRelatedDocument.objects.create(
                        source=rfctobe,
                        relationship=relationship,
                        target_rfctobe=target_rfctobe,
                    )
                except RfcToBe.DoesNotExist:
                    logger.warning(f"RFC {rfc_num} not found for updates relationship")

            updated_fields["obsoletes"] = obsoletes
            updated_fields["updates"] = updates

            # abstract
            # todo

            # authors
            # todo: implement author updates of affiliation, order and is_editor

            # publication status
            # todo

            # publication date
            pub_date = metadata.get("publication_date")
            if pub_date:
                year = int(pub_date.get("year"))
                month_str = pub_date.get("month")
                day = int(pub_date.get("day", 1))

                if not year or not month_str or not day:
                    raise ValueError("Incomplete publication date in metadata")

                # Convert month name to month number
                month = datetime.datetime.strptime(month_str, "%B").month

                rfctobe.published_at = datetime.datetime(year, month, day, 12, 0, 0)
                rfctobe.save(
                    update_fields=[
                        "published_at",
                    ]
                )
                updated_fields["published_at"] = rfctobe.published_at

            # subseries
            # Delete all existing subseries memberships
            SubseriesMember.objects.filter(rfc_to_be=rfctobe).delete()

            # Create new subseries memberships
            subseries = metadata.get("subseries", [])
            for subseries_item in subseries:
                # subseries_item is like {"name": "BCP", "value": "38"}
                type_slug = subseries_item.get("name", "").lower()
                number = subseries_item.get("value")

                if type_slug and number:
                    try:
                        subseries_type = SubseriesTypeName.objects.get(slug=type_slug)
                        SubseriesMember.objects.create(
                            rfc_to_be=rfctobe,
                            type=subseries_type,
                            number=int(number),
                        )
                    except SubseriesTypeName.DoesNotExist:
                        logger.warning(f"Subseries type {type_slug} not found")
                    except ValueError:
                        logger.warning(f"Invalid subseries number: {number}")

            updated_fields["subseries"] = subseries

        return updated_fields


class MetadataComparator:
    """Compare XML metadata with RfcToBe database values"""

    def __init__(self, rfc_to_be, xml_metadata):
        """
        Initialize comparator with RfcToBe instance and XML metadata dict.

        Args:
            rfc_to_be: RfcToBe instance
            xml_metadata: Dictionary containing parsed XML metadata
        """
        self.rfc_to_be = rfc_to_be
        self.xml_metadata = xml_metadata

    def compare_all(self):
        """
        Compare all metadata fields and return list of comparison results.

        Returns:
            List of comparison dicts, each containing:
            - field: field name
            - xml_value: value from XML
            - db_value: value from database
            - is_match: boolean indicating if values match
            - can_fix: boolean indicating if field can be auto-fixed (optional)
            - items: list of per-item comparisons for array fields (optional)
        """
        if not self.xml_metadata:
            return []

        return [
            self.compare_title(),
            self.compare_publication_date(),
            self.compare_authors(),
            self.compare_updates(),
            self.compare_obsoletes(),
            self.compare_subseries(),
        ]

    def compare_title(self):
        """Compare title field"""
        xml_value = self.xml_metadata.get("title", "")
        db_value = self.rfc_to_be.title or ""

        return {
            "field": "title",
            "xml_value": xml_value,
            "db_value": db_value,
            "is_match": xml_value == db_value,
            "can_fix": True,
        }

    def compare_publication_date(self):
        """Compare publication date field"""
        xml_date_obj = self.xml_metadata.get("publication_date", {})

        # Convert XML publication_date object to YYYY-mm-dd format
        xml_value = None
        if xml_date_obj:
            try:
                # Parse month name from XML to month number
                month_name = xml_date_obj.get("month", "")
                month_num = datetime.datetime.strptime(month_name, "%B").month
                year = xml_date_obj.get("year", "")
                day = xml_date_obj.get("day", "")
                xml_value = f"{year}-{month_num:02d}-{int(day):02d}"
            except (ValueError, KeyError):
                xml_value = None

        # Convert rfc_to_be.published_at to YYYY-mm-dd format
        db_value = None
        if self.rfc_to_be.published_at:
            db_value = self.rfc_to_be.published_at.strftime("%Y-%m-%d")

        return {
            "field": "publication_date",
            "xml_value": xml_value,
            "db_value": db_value,
            "is_match": xml_value == db_value,
            "can_fix": True,
        }

    def compare_authors(self):
        """Compare authors field with position-based comparison"""
        xml_value = self.xml_metadata.get("authors", [])

        db_author_parts = []
        for author in self.rfc_to_be.authors.all():
            author_name = author.titlepage_name or author.datatracker_person.plain_name
            if author.is_editor:
                author_name += ", Ed."
            if author.affiliation:
                author_name += f" ({author.affiliation})"
            db_author_parts.append(author_name)

        xml_author_parts = []
        for xml_author in xml_value:
            author_name = (
                xml_author.get("initials", "") + " " + xml_author.get("surname", "")
            )
            if xml_author.get("role", "").lower() == "editor":
                author_name += ", Ed."
            if xml_author.get("organization", ""):
                author_name += f" ({xml_author.get('organization')})"
            xml_author_parts.append(author_name)

        # Create items array with per-position comparison
        items = []
        overall_match = len(xml_author_parts) == len(db_author_parts)

        for xml_val, db_val in zip_longest(
            xml_author_parts, db_author_parts, fillvalue=""
        ):
            is_match = xml_val == db_val
            if not is_match:
                overall_match = False
            items.append(
                {
                    "is_match": is_match,
                    "xml_value": xml_val,
                    "db_value": db_val,
                }
            )

        return {
            "field": "authors",
            "is_match": overall_match,
            "items": items,
        }

    def compare_updates(self):
        """Compare updates field"""
        xml_value = self.xml_metadata.get("updates", [])

        db_value = list(
            self.rfc_to_be.rpcrelateddocument_set.filter(
                relationship__slug="updates"
            ).values_list("target_rfctobe__rfc_number", flat=True)
        )

        items = []
        overall_match = True

        for xml_ref, db_ref in zip_longest(xml_value, db_value, fillvalue=""):
            db_ref_str = str(db_ref) if db_ref else ""
            is_match = xml_ref == db_ref_str
            if not is_match:
                overall_match = False
            items.append(
                {
                    "is_match": is_match,
                    "xml_value": xml_ref,
                    "db_value": db_ref_str,
                }
            )

        return {
            "field": "updates",
            "is_match": overall_match,
            "items": items,
        }

    def compare_obsoletes(self):
        """Compare obsoletes field"""
        xml_value = self.xml_metadata.get("obsoletes", [])

        db_value = list(
            self.rfc_to_be.rpcrelateddocument_set.filter(
                relationship__slug="obs"
            ).values_list("target_rfctobe__rfc_number", flat=True)
        )

        items = []
        overall_match = True

        for xml_ref, db_ref in zip_longest(xml_value, db_value, fillvalue=""):
            db_ref_str = str(db_ref) if db_ref else ""
            is_match = xml_ref == db_ref_str
            if not is_match:
                overall_match = False
            items.append(
                {
                    "is_match": is_match,
                    "xml_value": xml_ref,
                    "db_value": db_ref_str,
                }
            )

        return {
            "field": "obsoletes",
            "is_match": overall_match,
            "items": items,
        }

    def compare_subseries(self):
        """Compare subseries field"""
        xml_value = self.xml_metadata.get("subseries", [])
        if not xml_value:
            xml_value = ""
        else:
            xml_value = xml_value[0]

        subseries_member = self.rfc_to_be.subseriesmember_set.first()
        if not subseries_member:
            db_value = ""
        else:
            db_value = f"{subseries_member.type.slug.upper()} {subseries_member.number}"

        return {
            "field": "subseries",
            "xml_value": xml_value,
            "db_value": db_value,
            "is_match": set(xml_value) == set(db_value),
        }

    def compare_abstract(self):
        """Compare abstract field"""
        xml_value = self.xml_metadata.get("abstract", "").strip()
        db_value = (
            (self.rfc_to_be.draft.abstract or "").strip()
            if self.rfc_to_be.draft
            else ""
        )

        return {
            "field": "abstract",
            "xml_value": xml_value,
            "db_value": db_value,
            "is_match": xml_value == db_value,
            "can_fix": True,
        }

    def can_fix(self):
        """
        Determine if all metadata fields can be auto-fixed.

        Returns:
            bool: True if all fields can be auto-fixed, False otherwise
        """
        comparisons = self.compare_all()
        for comparison in comparisons:
            if not comparison.get("can_fix", False):
                return False
        return True

    def is_match(self):
        """
        Determine if all metadata fields match.

        Returns:
            bool: True if all fields match, False otherwise
        """
        comparisons = self.compare_all()
        for comparison in comparisons:
            if not comparison.get("is_match", False):
                return False
        return True
