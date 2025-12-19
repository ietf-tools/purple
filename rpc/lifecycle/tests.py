# Copyright The IETF Trust 2025, All Rights Reserved
import jsonschema.exceptions
from django.test import TestCase

from .repo import Repository


class RepoTests(TestCase):
    def test_validate_manifest(self):
        repo = Repository()
        valid_manifest = {
            "publications": [
                {
                    "rfcNumber": 10000,
                    "files": [
                        {"type": "xml", "path": "toPublish/rfc10000.xml"},
                        {"type": "txt", "path": "toPublish/rfc10000.txt"},
                        {"type": "html", "path": "toPublish/rfc10000.html"},
                        {"type": "pdf", "path": "toPublish/rfc10000.pdf"},
                        {"type": "json", "path": "toPublish/rfc10000.json"},
                        {
                            "type": "notprepped",
                            "path": "toPublish/rfc10000.notprepped",
                        },
                    ],
                }
            ]
        }
        # Valid examples should not raise an exception
        try:
            repo.validate_manifest({"publications": []})  # empty publications array ok
            repo.validate_manifest(valid_manifest)  # actual valid publications is ok
            repo.validate_manifest(
                # valid publications manifest plus additional data is ok
                valid_manifest | {"someOtherKey": 27}
            )
        except Exception as err:
            # Treat exception as a fail rather than an error
            self.fail(f"Validation failed: {err}")

        # A couple invalid examples
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            repo.validate_manifest({})  # no publications
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            repo.validate_manifest({"someOtherKey": {}})  # still no publications
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            repo.validate_manifest(
                # no files
                {"publications": [{"rfcNumber": 10000}]}
            )
