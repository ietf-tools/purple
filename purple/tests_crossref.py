# Copyright The IETF Trust 2025, All Rights Reserved

from xml.etree.ElementTree import tostring

import responses
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import timezone
from requests.exceptions import HTTPError

from purple.crossref import (
    _generate_crossref_xml,
    _get_contributors,
    _get_name_parts,
    submit,
)
from rpc.factories import RfcAuthorFactory, RfcToBeFactory, StreamNameFactory


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
        DOI_AUTHOR_ORGS=[
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

    @override_settings(
        DOI_REGISTRANT="Mordor",
        DOI_DEPOSITOR="Sauron du Mordor",
        DOI_PREFIX="10.17487",
        DOI_EMAIL="sauron@example.org",
        DOI_URL="https://www.rfc-editor.org/scrolls/",
    )
    def test_generate_crossref_xml(self):
        RFC = 12345
        PUBLISHED = timezone.now()
        stream = StreamNameFactory.create(slug="ietf", name="IETF")
        rfc = RfcToBeFactory.create(
            rfc_number=RFC,
            title="The Book of Mazarbul",
            disposition__slug="published",
            published_at=PUBLISHED,
            stream=stream,
        )
        rfc_author_1 = RfcAuthorFactory.create(
            titlepage_name="A. Undómiel", is_editor=True
        )
        rfc_author_2 = RfcAuthorFactory.create(
            titlepage_name="L. Greenleaf", is_editor=False
        )
        rfc.authors.set([rfc_author_1, rfc_author_2])

        xml = _generate_crossref_xml(RFC)
        xml_str = tostring(xml, encoding="unicode")

        # registrant
        self.assertIn(f"<registrant>{settings.DOI_REGISTRANT}</registrant>", xml_str)

        # depositor
        self.assertIn(
            f"<depositor_name>{settings.DOI_DEPOSITOR}</depositor_name>", xml_str
        )
        self.assertIn(f"<email_address>{settings.DOI_EMAIL}</email_address>", xml_str)

        # first author
        first_author = xml.findall(".//person_name[@sequence='first']")
        self.assertEqual(len(first_author), 1)
        self.assertEqual(first_author[0].find(".//surname").text, "Undómiel")
        self.assertEqual(first_author[0].get("contributor_role"), "editor")

        # second author
        second_author = xml.findall(".//person_name[@sequence='additional']")
        self.assertEqual(len(second_author), 1)
        self.assertEqual(second_author[0].find(".//surname").text, "Greenleaf")
        self.assertEqual(second_author[0].get("contributor_role"), "author")

        # RFC metada
        self.assertIn(f"<title>{rfc.title}</title>", xml_str)
        self.assertIn(f"<month>{PUBLISHED.month}</month>", xml_str)
        self.assertIn(f"<year>{PUBLISHED.year}</year>", xml_str)
        self.assertIn(f"<item_number>RFC{RFC}</item_number>", xml_str)
        self.assertIn(f"<doi>{settings.DOI_PREFIX}/RFC{RFC}</doi>", xml_str)
        self.assertIn(f"<resource>{settings.DOI_URL}rfc{RFC}</resource>", xml_str)

    @override_settings(
        CROSSREF_API="https://test.crossref.org/servlet/deposit",
        CROSSREF_USER="sauron",
        CROSSREF_PASSWORD="mordor",
    )
    @responses.activate
    def test_submit(self):
        responses.add(responses.POST, settings.CROSSREF_API, status=200)

        RFC = 12345
        PUBLISHED = timezone.now()
        stream = StreamNameFactory.create(slug="ietf", name="IETF")
        rfc = RfcToBeFactory.create(
            rfc_number=RFC,
            title="The Book of Mazarbul",
            disposition__slug="published",
            published_at=PUBLISHED,
            stream=stream,
        )
        rfc_author_1 = RfcAuthorFactory.create(
            titlepage_name="A. Undómiel", is_editor=True
        )
        rfc_author_2 = RfcAuthorFactory.create(
            titlepage_name="L. Greenleaf", is_editor=False
        )
        rfc.authors.set([rfc_author_1, rfc_author_2])

        submit(RFC)

    @override_settings(
        CROSSREF_API="https://test.crossref.org/servlet/deposit",
        CROSSREF_USER="sauron",
        CROSSREF_PASSWORD="mordor",
    )
    @responses.activate
    def test_submit_error(self):
        responses.add(responses.POST, settings.CROSSREF_API, status=400)

        RFC = 12345
        PUBLISHED = timezone.now()
        stream = StreamNameFactory.create(slug="ietf", name="IETF")
        rfc = RfcToBeFactory.create(
            rfc_number=RFC,
            title="The Book of Mazarbul",
            disposition__slug="published",
            published_at=PUBLISHED,
            stream=stream,
        )
        rfc_author_1 = RfcAuthorFactory.create(
            titlepage_name="A. Undómiel", is_editor=True
        )
        rfc_author_2 = RfcAuthorFactory.create(
            titlepage_name="L. Greenleaf", is_editor=False
        )
        rfc.authors.set([rfc_author_1, rfc_author_2])

        with self.assertRaises(HTTPError):
            submit(RFC)
