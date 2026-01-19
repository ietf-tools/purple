# Copyright The IETF Trust 2026, All Rights Reserved
from django.test import TestCase

from .serializers import MetadataTableSerializer


class SerializerTests(TestCase):
    def test_metadata_table_serializer(self):
        INPUT_DATA = {
            "is_match": False,
            "can_autofix": False,
            "metadata_compare": [
                {
                    "field": "title",
                    "xml_value": (
                        "Applicability of Interfaces to Network Security Functions "
                        "to Network-Based Security Services"
                    ),
                    "db_value": (
                        "Applicability of Interfaces to Network Security Functions "
                        "to Network-Based Security Services"
                    ),
                    "is_match": True,
                },
                {
                    "field": "publication_date",
                    "xml_value": "2025-04-02",
                    "db_value": None,
                    "is_match": False,
                },
                {
                    "field": "authors",
                    "is_match": False,
                    "items": [
                        {
                            "is_match": False,
                            "xml_value": (
                                "J. Jeong (Department of Computer Science and "
                                "Engineering)"
                            ),
                            "db_value": "J. Jeong (Sungkyunkwan University)",
                        },
                        {
                            "is_match": False,
                            "xml_value": "S. Hyun (Department of Computer Engineering)",
                            "db_value": "S. Hyun (Myongji University)",
                        },
                        {
                            "is_match": False,
                            "xml_value": "T. Ahn (KT)",
                            "db_value": "T. Ahn (Korea Telecom)",
                        },
                        {
                            "is_match": True,
                            "xml_value": "S. Hares (Huawei)",
                            "db_value": "S. Hares (Huawei)",
                        },
                        {
                            "is_match": True,
                            "xml_value": "D. Lopez (Telefonica I+D)",
                            "db_value": "D. Lopez (Telefonica I+D)",
                        },
                    ],
                },
            ],
        }
        EXPECTED_OUTPUT = {
            "rfc_to_be": 12345,
            "repository": "some/repo",
            "head_sha": "deadbeef",
            "can_autofix": False,
            "is_match": False,
            "metadata_compare": [
                {
                    "row_name": "title",
                    "row_name_list_depth": 0,
                    "row_value": {
                        "left_value": (
                            "Applicability of Interfaces to Network Security Functions "
                            "to Network-Based Security Services"
                        ),
                        "right_value": (
                            "Applicability of Interfaces to Network Security Functions "
                            "to Network-Based Security Services"
                        ),
                        "is_match": True,
                    },
                },
                {
                    "row_name": "publication_date",
                    "row_name_list_depth": 0,
                    "row_value": {
                        "left_value": "",
                        "right_value": "2025-04-02",
                        "is_match": False,
                    },
                },
                {
                    "row_name": "authors",
                    "row_name_list_depth": 0,
                    "row_value": {
                        "left_value": "",
                        "right_value": "",
                        "is_match": False,
                    },
                },
                {
                    "row_name": "",
                    "row_name_list_depth": 1,
                    "row_value": {
                        "left_value": "J. Jeong (Sungkyunkwan University)",
                        "right_value": (
                            "J. Jeong (Department of Computer Science and Engineering)"
                        ),
                        "is_match": False,
                    },
                },
                {
                    "row_name": "",
                    "row_name_list_depth": 1,
                    "row_value": {
                        "left_value": "S. Hyun (Myongji University)",
                        "right_value": "S. Hyun (Department of Computer Engineering)",
                        "is_match": False,
                    },
                },
                {
                    "row_name": "",
                    "row_name_list_depth": 1,
                    "row_value": {
                        "left_value": "T. Ahn (Korea Telecom)",
                        "right_value": "T. Ahn (KT)",
                        "is_match": False,
                    },
                },
                {
                    "row_name": "",
                    "row_name_list_depth": 1,
                    "row_value": {
                        "left_value": "S. Hares (Huawei)",
                        "right_value": "S. Hares (Huawei)",
                        "is_match": True,
                    },
                },
                {
                    "row_name": "",
                    "row_name_list_depth": 1,
                    "row_value": {
                        "left_value": "D. Lopez (Telefonica I+D)",
                        "right_value": "D. Lopez (Telefonica I+D)",
                        "is_match": True,
                    },
                },
            ],
        }
        self.assertEqual(
            dict(MetadataTableSerializer(INPUT_DATA).data), EXPECTED_OUTPUT
        )
