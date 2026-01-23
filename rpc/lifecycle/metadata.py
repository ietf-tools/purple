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
        """Update metadata fields from metadata dictionary

        First compares all fields to see what needs to be updated,
        then selectively updates only those fields that differ and can be auto-fixed.
        """

        updated_fields = {}

        # First, compare all fields to see what needs to be updated
        comparator = MetadataComparator(rfctobe, metadata)
        comparisons = comparator.compare_all()

        with transaction.atomic():
            # Process each comparison result
            for comparison in comparisons:
                field = comparison["field"]
                is_match = comparison["is_match"]
                can_fix = comparison["can_fix"]

                if not is_match and can_fix:
                    if field == "title":
                        new_title = metadata.get("title")
                        if new_title:
                            rfctobe.title = new_title
                            rfctobe.save(update_fields=["title"])
                            updated_fields["title"] = new_title

                    elif field == "abstract":
                        new_abstract = metadata.get("abstract")
                        if new_abstract:
                            rfctobe.abstract = new_abstract
                            rfctobe.save(update_fields=["abstract"])
                            updated_fields["abstract"] = new_abstract

                    elif field == "updates":
                        # Delete existing updates relationships
                        RpcRelatedDocument.objects.filter(
                            source=rfctobe, relationship__slug="updates"
                        ).delete()

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
                                logger.warning(
                                    f"RFC {rfc_num} not found for updates relationship"
                                )
                        updated_fields["updates"] = updates

                    elif field == "obsoletes":
                        # Delete existing obsoletes relationships
                        RpcRelatedDocument.objects.filter(
                            source=rfctobe, relationship__slug="obs"
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
                                    f"RFC {rfc_num} not found for obsolete relationship"
                                )
                        updated_fields["obsoletes"] = obsoletes

                    elif field == "authors":
                        # Update author affiliation and is_editor role where they differ
                        xml_authors = metadata.get("authors", [])
                        db_authors = list(rfctobe.authors.all().order_by("order"))

                        # Validate that lengths match and names match at each position
                        if len(xml_authors) != len(db_authors):
                            raise ValueError(
                                f"Author length mismatch: XML has {len(xml_authors)} "
                                f"authors, DB has {len(db_authors)} authors"
                            )

                        for position, (xml_author, db_author) in enumerate(
                            zip_longest(xml_authors, db_authors, fillvalue=None)
                        ):
                            if xml_author is None or db_author is None:
                                raise ValueError(
                                    f"Unexpected None value at position {position} "
                                    "during author update"
                                )

                            # Verify names match
                            xml_name = (
                                xml_author.get("initials", "")
                                + " "
                                + xml_author.get("surname", "")
                            ).strip()
                            db_name = db_author.titlepage_name
                            if xml_name != db_name:
                                raise ValueError(
                                    f"Author name mismatch at position {position}: "
                                    f"XML='{xml_name}', DB='{db_name}'"
                                )

                            # Update affiliation if different
                            xml_org = xml_author.get("organization", "").strip()
                            if xml_org != (db_author.affiliation or ""):
                                db_author.affiliation = xml_org
                                db_author.save(update_fields=["affiliation"])
                                if "authors" not in updated_fields:
                                    updated_fields["authors"] = []
                                updated_fields["authors"].append(
                                    {
                                        "position": position,
                                        "name": db_author.titlepage_name
                                        or db_author.datatracker_person.plain_name,
                                        "affiliation": xml_org,
                                    }
                                )

                            # Update is_editor if different
                            xml_is_editor = (
                                xml_author.get("role", "").lower() == "editor"
                            )
                            if xml_is_editor != db_author.is_editor:
                                db_author.is_editor = xml_is_editor
                                db_author.save(update_fields=["is_editor"])
                                if "authors" not in updated_fields:
                                    updated_fields["authors"] = []
                                # Check if we already added author to updated_fields
                                author_entry = next(
                                    (
                                        a
                                        for a in updated_fields["authors"]
                                        if a["position"] == position
                                    ),
                                    None,
                                )
                                if author_entry:
                                    author_entry["is_editor"] = xml_is_editor
                                else:
                                    updated_fields["authors"].append(
                                        {
                                            "position": position,
                                            "name": db_author.titlepage_name
                                            or db_author.datatracker_person.plain_name,
                                            "is_editor": xml_is_editor,
                                        }
                                    )

                    elif field == "subseries":
                        # Delete all existing subseries memberships
                        SubseriesMember.objects.filter(rfc_to_be=rfctobe).delete()

                        # Create new subseries memberships
                        subseries = metadata.get("subseries", [])
                        for subseries_item in subseries:
                            type_slug = subseries_item.get("name", "").lower()
                            number = subseries_item.get("value")

                            if type_slug and number:
                                try:
                                    subseries_type = SubseriesTypeName.objects.get(
                                        slug=type_slug
                                    )
                                    SubseriesMember.objects.create(
                                        rfc_to_be=rfctobe,
                                        type=subseries_type,
                                        number=int(number),
                                    )
                                except SubseriesTypeName.DoesNotExist:
                                    logger.warning(
                                        f"Subseries type {type_slug} not found"
                                    )
                                except ValueError:
                                    logger.warning(
                                        f"Invalid subseries number: {number}"
                                    )

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
            self.compare_authors(),
            self.compare_updates(),
            self.compare_obsoletes(),
            self.compare_subseries(),
            self.compare_abstract(),
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

    def compare_authors(self):
        """Compare authors field with position-based comparison.

        Author names must match exactly. If names match, organization and editor role
        differences are considered fixable. If names don't match, it's not fixable.
        """
        xml_value = self.xml_metadata.get("authors", [])
        db_authors = list(self.rfc_to_be.authors.all().order_by("order"))

        # Create items array with per-position comparison
        items = []
        overall_match = len(xml_value) == len(db_authors)
        overall_can_fix = True

        for position, (xml_author, db_author) in enumerate(
            zip_longest(xml_value, db_authors, fillvalue=None)
        ):
            item = {"position": position}

            if xml_author is None or db_author is None:
                # Mismatched lengths - cannot fix
                item["is_match"] = False
                item["can_fix"] = False
                overall_match = False
                overall_can_fix = False
                items.append(item)
                continue

            # Extract author names
            xml_name = (
                xml_author.get("initials", "") + " " + xml_author.get("surname", "")
            ).strip()
            db_name = db_author.titlepage_name

            # Check if names match
            if xml_name != db_name:
                # Names don't match - not fixable
                item["is_match"] = False
                item["can_fix"] = False
                item["xml_value"] = xml_name
                item["db_value"] = db_name
                overall_match = False
                overall_can_fix = False
                items.append(item)
                continue

            # Names match, now check organization and editor role
            xml_org = xml_author.get("organization", "").strip()
            db_org = (db_author.affiliation or "").strip()
            xml_is_editor = xml_author.get("role", "").lower() == "editor"
            db_is_editor = db_author.is_editor

            org_match = xml_org == db_org
            editor_match = xml_is_editor == db_is_editor

            if xml_is_editor:
                xml_name += " , Ed."
            if db_is_editor:
                db_name += " , Ed."
            if xml_org:
                xml_name += f" ({xml_org})"
            if db_org:
                db_name += f" ({db_org})"
            item["xml_value"] = xml_name
            item["db_value"] = db_name
            item["name_match"] = True

            if org_match and editor_match:
                # Everything matches
                item["is_match"] = True
                item["can_fix"] = True
            else:
                # Name matches but organization or editor role differs - fixable
                item["is_match"] = False
                item["can_fix"] = True
                overall_match = False

            items.append(item)

        return {
            "field": "authors",
            "is_match": overall_match,
            "can_fix": overall_can_fix,
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
            "can_fix": True,
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
            "can_fix": True,
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
            "can_fix": True,
        }

    def compare_abstract(self):
        """Compare abstract field"""
        xml_value = self.xml_metadata.get("abstract", "").strip()
        db_value = (self.rfc_to_be.abstract or "").strip()

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
            bool: True if all fields can be auto-fixed, and NOT all match,
            False otherwise
        """
        comparisons = self.compare_all()
        for comparison in comparisons:
            if not comparison.get("can_fix", False):
                return False
        return not self.is_match()

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
