# Copyright The IETF Trust 2025, All Rights Reserved

from xml.etree.ElementTree import tostring

from django.test import TestCase, override_settings

from purple.crossref import _get_contributors, _get_name_parts
from rpc.factories import RfcAuthorFactory


class CrossrefTests(TestCase):
    def setUp(self):
        self.names = {
            "Legolas Greenleaf": ("Legolas", "Greenleaf", ""),
            "A. Undómiel": ("A.", "Undómiel", ""),
            "Aragorn Elessar 2nd": ("Aragorn", "Elessar", "2nd"),
            "Théoden van Ednew": ("Théoden", "van Ednew", ""),
            "Q": ("", "Q", ""),  # crossref requires a surname
            "Saruman": ("", "Saruman", ""),
        }

    def test_get_name_parts(self):
        for name, name_parts in self.names.items():
            self.assertEqual(_get_name_parts(name), name_parts)

    def test_get_contributors(self):
        for name, name_parts in self.names.items():
            rfc_author = RfcAuthorFactory.build(titlepage_name=name)
            xml_str = tostring(
                _get_contributors(rfc_author, "additional"), encoding="unicode"
            )

            self.assertIn("additional", xml_str)
            self.assertIn("author", xml_str)
            self.assertIn(f"<surname>{name_parts[1]}</surname>", xml_str)
            if name_parts[0]:
                self.assertIn(f"<given_name>{name_parts[0]}</given_name>", xml_str)
            if name_parts[2]:
                self.assertIn(f"<suffix>{name_parts[2]}</suffix>", xml_str)

    @override_settings(
        AUTHOR_ORGS=[
            "Rohan",
        ]
    )
    def test_get_contributors_orgs(self):
        rfc_author = RfcAuthorFactory.build(titlepage_name="Rohan")
        xml_str = tostring(_get_contributors(rfc_author, "first"), encoding="unicode")

        self.assertIn("first", xml_str)
        self.assertIn("Rohan</organization>", xml_str)

    def test_get_contributors_editor(self):
        rfc_author = RfcAuthorFactory.build(
            titlepage_name="A. Undómiel", is_editor=True
        )
        xml_str = tostring(_get_contributors(rfc_author, "first"), encoding="unicode")

        self.assertIn("first", xml_str)
        self.assertIn("editor", xml_str)
        self.assertIn("<surname>Undómiel</surname>", xml_str)
