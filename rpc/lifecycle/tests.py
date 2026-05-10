# Copyright The IETF Trust 2025-2026, All Rights Reserved
import logging
from unittest.mock import MagicMock, patch

import jsonschema.exceptions
from django.test import TestCase
from rest_framework import serializers

from rpc.factories import PublicationAttemptFactory, RfcToBeFactory
from rpc.models import PublicationAttempt, RfcToBe

from .publication import (
    AmbiguousFilesError,
    MissingFilesError,
    PublicationError,
    _do_publish_rfctobe,
    begin_publication_attempt,
    choose_files,
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

        # it's now FAILED - calling again overwrites the detail
        # (task re-run after worker restart)
        record_failed_publication_attempt(rfc_to_be, "worse mojo")
        rfc_to_be.publicationattempt.refresh_from_db()
        self.assertEqual(
            rfc_to_be.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertEqual(rfc_to_be.publicationattempt.detail, "worse mojo")

        # and now try from PENDING
        PublicationAttempt.objects.filter(rfc_to_be=rfc_to_be).update(
            status=PublicationAttempt.Status.PENDING,
            detail="",
        )
        record_failed_publication_attempt(rfc_to_be, "bad mojo")
        rfc_to_be.publicationattempt.refresh_from_db()
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


ALL_FILES = [
    {"type": "xml", "path": "rfc10000.xml"},
    {"type": "txt", "path": "rfc10000.txt"},
    {"type": "html", "path": "rfc10000.html"},
    {"type": "pdf", "path": "rfc10000.pdf"},
    {"type": "notprepped", "path": "rfc10000.notprepped.xml"},
]


class ChooseFilesTests(TestCase):
    def test_valid(self):
        result = choose_files(ALL_FILES)
        self.assertEqual(result["xml"], "rfc10000.xml")
        self.assertEqual(result["txt"], "rfc10000.txt")
        self.assertEqual(result["html"], "rfc10000.html")
        self.assertEqual(result["pdf"], "rfc10000.pdf")
        self.assertEqual(result["notprepped"], "rfc10000.notprepped.xml")

    def test_missing_file_raises(self):
        # Only xml present — all others missing
        with self.assertRaises(MissingFilesError):
            choose_files([{"type": "xml", "path": "rfc10000.xml"}])

    def test_missing_single_file_raises(self):
        # All but pdf
        files = [f for f in ALL_FILES if f["type"] != "pdf"]
        with self.assertRaises(MissingFilesError) as ctx:
            choose_files(files)
        self.assertIn("pdf", str(ctx.exception))

    def test_ambiguous_file_raises(self):
        files = ALL_FILES + [{"type": "xml", "path": "rfc10000-v2.xml"}]
        with self.assertRaises(AmbiguousFilesError) as ctx:
            choose_files(files)
        self.assertIn("xml", str(ctx.exception))


class PublishRfcToBeTests(TestCase):
    RFC_NUMBER = 10000
    EXPECTED_HEAD = "abc1234"

    def _make_rfctobe(self):
        return RfcToBeFactory(rfc_number=self.RFC_NUMBER, repository="org/repo")

    def _make_mock_repo(self, files):
        mock_repo = MagicMock()
        mock_repo.ref = self.EXPECTED_HEAD
        mock_repo.get_manifest.return_value = {
            "publications": [{"rfcNumber": self.RFC_NUMBER, "files": files}]
        }
        return mock_repo

    def test_validation_failure_marks_attempt_failed(self):
        rfctobe = self._make_rfctobe()
        PublicationAttempt.objects.create(
            rfc_to_be=rfctobe, status=PublicationAttempt.Status.PENDING
        )

        with (
            patch(
                "rpc.lifecycle.publication.validate_ready_to_publish",
                side_effect=serializers.ValidationError(
                    {"non_field_errors": "no publisher assigned"},
                    code="rfctobe-no-publisher",
                ),
            ),
            patch("rpc.lifecycle.publication.GithubRepository"),
        ):
            _do_publish_rfctobe(rfctobe, self.EXPECTED_HEAD, rpcapi=MagicMock())

        rfctobe.publicationattempt.refresh_from_db()
        self.assertEqual(
            rfctobe.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertIn("no publisher assigned", rfctobe.publicationattempt.detail)

    def test_missing_files_marks_attempt_failed(self):
        rfctobe = self._make_rfctobe()
        PublicationAttempt.objects.create(
            rfc_to_be=rfctobe, status=PublicationAttempt.Status.PENDING
        )
        mock_repo = self._make_mock_repo(
            [
                {"type": "xml", "path": "rfc10000.xml"}
            ]  # missing txt, html, pdf, notprepped
        )
        with (
            patch("rpc.lifecycle.publication.validate_ready_to_publish"),
            patch("rpc.lifecycle.publication.GithubRepository", return_value=mock_repo),
        ):
            _do_publish_rfctobe(rfctobe, self.EXPECTED_HEAD, rpcapi=MagicMock())

        rfctobe.publicationattempt.refresh_from_db()
        self.assertEqual(
            rfctobe.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertIn("Missing files", rfctobe.publicationattempt.detail)

    def test_ambiguous_files_marks_attempt_failed(self):
        rfctobe = self._make_rfctobe()
        PublicationAttempt.objects.create(
            rfc_to_be=rfctobe, status=PublicationAttempt.Status.PENDING
        )
        mock_repo = self._make_mock_repo(
            ALL_FILES + [{"type": "xml", "path": "rfc10000-alt.xml"}]
        )
        with (
            patch("rpc.lifecycle.publication.validate_ready_to_publish"),
            patch("rpc.lifecycle.publication.GithubRepository", return_value=mock_repo),
        ):
            _do_publish_rfctobe(rfctobe, self.EXPECTED_HEAD, rpcapi=MagicMock())

        rfctobe.publicationattempt.refresh_from_db()
        self.assertEqual(
            rfctobe.publicationattempt.status, PublicationAttempt.Status.FAILED
        )
        self.assertIn("More than one of", rfctobe.publicationattempt.detail)

    def test_upload_failure_raises_publication_error(self):
        """After publish_rfc_metadata succeeds, upload failure raises
        PublicationError."""
        rfctobe = self._make_rfctobe()
        PublicationAttempt.objects.create(
            rfc_to_be=rfctobe, status=PublicationAttempt.Status.PENDING
        )

        mock_repo = self._make_mock_repo(ALL_FILES)
        mock_repo.get_file.return_value.__enter__ = MagicMock()
        mock_repo.get_file.return_value.__exit__ = MagicMock(return_value=False)
        mock_repo.get_file.return_value.chunks.return_value = [b"data"]

        with (
            patch("rpc.lifecycle.publication.validate_ready_to_publish"),
            patch("rpc.lifecycle.publication.GithubRepository", return_value=mock_repo),
            patch("rpc.lifecycle.publication.publish_rfc_metadata"),
            patch(
                "rpc.lifecycle.publication.upload_rfc_contents",
                side_effect=RuntimeError("upload failed"),
            ),
            patch("rpc.lifecycle.publication.create_rfc_index_json"),
            self.assertRaises(PublicationError) as ctx,
        ):
            _do_publish_rfctobe(rfctobe, self.EXPECTED_HEAD, rpcapi=MagicMock())

        self.assertIn("uploading its files failed", str(ctx.exception))
