# Copyright The IETF Trust 2025-2026, All Rights Reserved
import logging

import jsonschema.exceptions
from django.test import TestCase

from rpc.factories import PublicationAttemptFactory, RfcToBeFactory
from rpc.models import PublicationAttempt, RfcToBe

from .publication import (
    begin_publication_attempt,
    clear_publication_attempt,
    record_failed_publication_attempt,
)
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


class PublicationTests(TestCase):
    def test_begin_publication_attempt(self):
        rfc_to_be = RfcToBeFactory()
        assert isinstance(rfc_to_be, RfcToBe)
        self.assertIsNone(
            PublicationAttempt.objects.filter(rfc_to_be=rfc_to_be).first()
        )

        # nothing happening yet
        already_pending = begin_publication_attempt(rfc_to_be)
        self.assertFalse(already_pending)
        self.assertEqual(
            rfc_to_be.publicationattempt.status,
            PublicationAttempt.Status.PENDING,
        )

        # already pending now
        already_pending = begin_publication_attempt(rfc_to_be)
        self.assertTrue(already_pending)
        self.assertEqual(
            rfc_to_be.publicationattempt.status,
            PublicationAttempt.Status.PENDING,
        )

        # recover from failed attempt
        PublicationAttempt.objects.filter(rfc_to_be=rfc_to_be).update(
            status=PublicationAttempt.Status.FAILED
        )
        already_pending = begin_publication_attempt(rfc_to_be)
        self.assertFalse(already_pending)
        self.assertEqual(
            rfc_to_be.publicationattempt.status,
            PublicationAttempt.Status.PENDING,
        )

    def test_record_failed_publication_attempt(self):
        logging.disable(logging.WARNING)  # squelch warnings
        rfc_to_be = RfcToBeFactory()
        assert isinstance(rfc_to_be, RfcToBe)

        # normally we'd have a PENDING state already, but it should work even if
        # not, so let's test that way - it's easier
        record_failed_publication_attempt(rfc_to_be, "bad mojo")
        self.assertEqual(
            rfc_to_be.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertEqual(rfc_to_be.publicationattempt.detail, "bad mojo")

        # it's now FAILED - updating again should not disturb that
        record_failed_publication_attempt(rfc_to_be, "worse mojo")
        self.assertEqual(
            rfc_to_be.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertEqual(rfc_to_be.publicationattempt.detail, "bad mojo")

        # and now try from PENDING
        PublicationAttempt.objects.filter(rfc_to_be=rfc_to_be).update(
            status=PublicationAttempt.Status.PENDING,
            detail="",
        )
        record_failed_publication_attempt(rfc_to_be, "bad mojo")
        self.assertEqual(
            rfc_to_be.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertEqual(rfc_to_be.publicationattempt.detail, "bad mojo")
        logging.disable(logging.NOTSET)

    def test_clear_failed_publication_attempt(self):
        rfctobes = [pa.rfc_to_be for pa in PublicationAttemptFactory.create_batch(2)]
        self.assertEqual(PublicationAttempt.objects.count(), 2)
        clear_publication_attempt(rfctobes[0])
        self.assertEqual(PublicationAttempt.objects.count(), 1)
        self.assertEqual(PublicationAttempt.objects.first().rfc_to_be, rfctobes[1])
