# Copyright The IETF Trust 2026, All Rights Reserved
from django.test import TestCase

from .metadata import Metadata


class MetadataTests(TestCase):
    def test_extract_name_from_author_dict(self):
        self.assertEqual(
            Metadata.extract_name_from_author_dict({}), "", "empty input dict"
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"initials": " A. B. "}),
            "A. B.",
            "initials only plus stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"surname": " Clyde "}),
            "Clyde",
            "surname only plus stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"initials": " A. B. ", "surname": " Clyde"}
            ),
            "A. B. Clyde",
            "initials+surname + stripping",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {
                    "initials": "A. B.",
                    "surname": "Clyde",
                    "fullname": "Diane Egawa",
                    "asciiFullname": "Frank Gouda",
                }
            ),
            "A. B. Clyde",
            "initials+surname have priority",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"fullname": "Diane Egawa", "asciiFullname": "Frank Gouda"}
            ),
            "F. Gouda",
            "asciiFullname has priority",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict(
                {"fullname": "Diane Egawa", "asciiFullname": "Gouda"}
            ),
            "Gouda",
            "asciiFullname has priority + single name",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "Diane Egawa"}),
            "D. Egawa",
            "fullname with two names",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "Egawa"}),
            "Egawa",
            "fullname with one name",
        )
        self.assertEqual(
            Metadata.extract_name_from_author_dict({"fullname": "江川"}),
            "江川",
            "fullname with one name",
        )
