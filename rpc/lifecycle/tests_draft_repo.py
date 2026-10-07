# Copyright The IETF Trust 2026, All Rights Reserved
import base64
from types import SimpleNamespace
from unittest import mock

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from github import GithubException, UnknownObjectException
from rpcapi_client.exceptions import ApiException

from rpc.factories import RfcToBeFactory, RpcPersonFactory
from rpc.models import Notification
from rpc.tasks import create_draft_repo_task, create_draft_repos_task

from .draft_repo import DraftRepoError, DraftRepoExists, create_draft_repo, is_enabled

NAME = "draft-ietf-foo-bar"
FULL_NAME = f"rfc-editor-drafts/{NAME}"


def _response(status_code, content=b""):
    response = mock.Mock(status_code=status_code, content=content)
    response.ok = status_code < 400
    return response


@override_settings(
    GITHUB_DRAFTS_WRITE_TOKEN="write-token", GITHUB_DRAFTS_ORG="rfc-editor-drafts"
)
class CreateDraftRepoTests(TestCase):
    def setUp(self):
        self.rfc_to_be = RfcToBeFactory(
            draft__name=NAME, rev="03", title="Foo Bar Protocol", repository=""
        )
        self.archive = {
            f"https://www.ietf.org/archive/id/{NAME}-03.txt": _response(200, b"txt"),
            f"https://www.ietf.org/archive/id/{NAME}-03.xml": _response(200, b"<x/>"),
        }
        get = mock.patch(
            "rpc.lifecycle.draft_repo.requests.get",
            side_effect=lambda url, **kwargs: self.archive[url],
        )
        self.get = get.start()
        self.addCleanup(get.stop)

        github = mock.patch("rpc.lifecycle.draft_repo.Github")
        self.github = github.start().return_value
        self.addCleanup(github.stop)
        self.org = self.github.get_organization.return_value
        self.org.get_repo.side_effect = UnknownObjectException(404)
        self.repo = self.org.create_repo_from_template.return_value
        self.repo.full_name = FULL_NAME
        self.ref = self.repo.get_git_ref.return_value
        self.blobs = {}

        def create_blob(content, encoding):
            sha = f"blob-{len(self.blobs)}"
            self.blobs[sha] = base64.b64decode(content)
            return mock.Mock(sha=sha)

        self.repo.create_git_blob.side_effect = create_blob

        element = mock.patch(
            "rpc.lifecycle.draft_repo.InputGitTreeElement",
            side_effect=lambda path, mode, type, sha: SimpleNamespace(
                path=path, mode=mode, type=type, sha=sha
            ),
        )
        element.start()
        self.addCleanup(element.stop)

        sleep = mock.patch("rpc.lifecycle.draft_repo.time.sleep")
        sleep.start()
        self.addCleanup(sleep.stop)

    def committed_files(self):
        (elements, _base), _ = self.repo.create_git_tree.call_args
        return {e.path: self.blobs[e.sha] for e in elements}

    def test_creates_and_populates_the_repo(self):
        self.assertEqual(create_draft_repo(self.rfc_to_be), FULL_NAME)

        self.github.get_repo.assert_called_with("rfc-editor-drafts/base-template")
        self.org.create_repo_from_template.assert_called_once_with(
            NAME,
            self.github.get_repo.return_value,
            description="Foo Bar Protocol",
            private=True,
        )
        self.repo.get_git_ref.assert_called_with("heads/Approved")
        self.assertEqual(
            self.committed_files(),
            {
                "README.md": f"# {NAME}\n".encode(),
                f"{NAME}-03.txt": b"txt",
                f"{NAME}-03.original": b"txt",
                f"{NAME}-03.xml": b"<x/>",
                f"{NAME}-03.original.xml": b"<x/>",
            },
        )
        message, _tree, parents = self.repo.create_git_commit.call_args.args
        self.assertEqual(message, "approved I-D")
        self.assertEqual(parents, [self.repo.get_git_commit.return_value])
        self.ref.edit.assert_called_once_with(
            self.repo.create_git_commit.return_value.sha
        )
        self.rfc_to_be.refresh_from_db()
        self.assertEqual(self.rfc_to_be.repository, FULL_NAME)

    @override_settings(GITHUB_DRAFTS_ORG="rfc-editor-drafts-staging")
    def test_uses_the_configured_organization(self):
        self.repo.full_name = f"rfc-editor-drafts-staging/{NAME}"
        create_draft_repo(self.rfc_to_be)
        self.github.get_organization.assert_called_with("rfc-editor-drafts-staging")
        self.github.get_repo.assert_called_with(
            "rfc-editor-drafts-staging/base-template"
        )

    def test_existing_repo_aborts(self):
        self.org.get_repo.side_effect = None
        with self.assertRaisesMessage(DraftRepoExists, f"{FULL_NAME} already exists"):
            create_draft_repo(self.rfc_to_be)
        self.org.create_repo_from_template.assert_not_called()

    def test_missing_file_aborts_before_github(self):
        self.archive[f"https://www.ietf.org/archive/id/{NAME}-03.xml"] = _response(404)
        with self.assertRaisesMessage(
            DraftRepoError, f"{NAME}-03.xml is not in the IETF archive"
        ):
            create_draft_repo(self.rfc_to_be)
        self.github.get_organization.assert_not_called()

    def test_unreachable_archive_aborts(self):
        self.get.side_effect = requests.ConnectionError()
        with self.assertRaisesMessage(
            DraftRepoError, "Could not reach the IETF archive"
        ):
            create_draft_repo(self.rfc_to_be)

    def test_github_error_aborts(self):
        self.org.create_repo_from_template.side_effect = GithubException(503)
        with self.assertRaisesMessage(DraftRepoError, "GitHub failed while creating"):
            create_draft_repo(self.rfc_to_be)
        self.rfc_to_be.refresh_from_db()
        self.assertEqual(self.rfc_to_be.repository, "")

    def test_waits_while_github_still_fills_the_new_repo(self):
        """GitHub returns 409 ("Git Repository is empty") until it has populated a
        repository created from a template."""
        self.repo.get_git_ref.side_effect = [
            GithubException(409, {"message": "Git Repository is empty."}),
            UnknownObjectException(404),
            self.ref,
        ]
        self.assertEqual(create_draft_repo(self.rfc_to_be), FULL_NAME)
        self.assertEqual(self.repo.get_git_ref.call_count, 3)
        self.ref.edit.assert_called_once()

    def test_other_github_errors_while_waiting_abort(self):
        self.repo.get_git_ref.side_effect = GithubException(500)
        with self.assertRaisesMessage(DraftRepoError, "GitHub failed while creating"):
            create_draft_repo(self.rfc_to_be)
        self.assertEqual(self.repo.get_git_ref.call_count, 1)

    def test_branch_that_never_appears_aborts(self):
        self.repo.get_git_ref.side_effect = UnknownObjectException(404)
        with self.assertRaisesMessage(DraftRepoError, "Approved branch never appeared"):
            create_draft_repo(self.rfc_to_be)
        self.repo.create_git_commit.assert_not_called()

    def test_document_without_revision_aborts(self):
        self.rfc_to_be.rev = ""
        with self.assertRaisesMessage(DraftRepoError, "has no revision"):
            create_draft_repo(self.rfc_to_be)


class IsEnabledTests(TestCase):
    @override_settings(GITHUB_DRAFTS_WRITE_TOKEN=None)
    def test_off_without_a_write_token(self):
        self.assertFalse(is_enabled())

    @override_settings(GITHUB_DRAFTS_WRITE_TOKEN="write-token")
    def test_on_with_a_write_token(self):
        self.assertTrue(is_enabled())


class CreateDraftRepoTaskTests(TestCase):
    def setUp(self):
        self.rfc_to_be = RfcToBeFactory(draft__name=NAME)
        self.importer = RpcPersonFactory()
        self.user = get_user_model().objects.create_user(username="importer")
        patcher = mock.patch(
            "rpcauth.models.User.rpcperson", return_value=self.importer
        )
        self.rpcperson = patcher.start()
        self.addCleanup(patcher.stop)

    @mock.patch("rpc.tasks.create_draft_repo", return_value=FULL_NAME)
    def test_success_is_not_notified(self, _create):
        create_draft_repo_task(self.rfc_to_be.pk, self.user.pk)
        self.assertFalse(Notification.objects.exists())

    @mock.patch(
        "rpc.tasks.create_draft_repo",
        side_effect=DraftRepoError(
            "draft-ietf-foo-bar-03.xml is not in the IETF archive"
        ),
    )
    def test_other_failures_have_no_manual_fix_hint(self, _create):
        create_draft_repo_task(self.rfc_to_be.pk, self.user.pk)
        self.assertNotIn("manual fix", Notification.objects.get().message)

    @mock.patch(
        "rpc.tasks.create_draft_repo",
        side_effect=DraftRepoExists(f"{FULL_NAME} already exists"),
    )
    def test_tells_the_importer_why_not(self, _create):
        create_draft_repo_task(self.rfc_to_be.pk, self.user.pk)
        notification = Notification.objects.get()
        self.assertEqual(notification.event_type, "repo_not_created")
        self.assertEqual(notification.recipient, self.importer)
        self.assertEqual(
            notification.message,
            f"No repo created for {NAME}: {FULL_NAME} already exists"
            " (needs manual fix)",
        )

    @mock.patch(
        "rpc.tasks.create_draft_repo",
        side_effect=DraftRepoError(f"{FULL_NAME} already exists"),
    )
    def test_without_an_importer_tells_everyone(self, _create):
        create_draft_repo_task(self.rfc_to_be.pk, None)
        self.assertIsNone(Notification.objects.get().recipient)

    @mock.patch(
        "rpc.tasks.create_draft_repo",
        side_effect=DraftRepoError(f"{FULL_NAME} already exists"),
    )
    def test_an_unreachable_datatracker_tells_everyone(self, _create):
        self.rpcperson.side_effect = ApiException(status=503)
        with self.assertLogs("rpc.tasks", level="WARNING"):
            create_draft_repo_task(self.rfc_to_be.pk, self.user.pk)
        self.assertIsNone(Notification.objects.get().recipient)

    @mock.patch(
        "rpc.tasks.create_draft_repo",
        side_effect=DraftRepoError(f"{FULL_NAME} already exists"),
    )
    def test_other_errors_looking_up_the_importer_are_raised(self, _create):
        self.rpcperson.side_effect = RuntimeError("bug")
        with self.assertRaises(RuntimeError):
            create_draft_repo_task(self.rfc_to_be.pk, self.user.pk)


@override_settings(GITHUB_DRAFTS_WRITE_TOKEN="write-token")
@mock.patch("rpc.api.create_draft_repo_task")
class CreateRepoActionTests(TestCase):
    """POST /api/rpc/documents/<name>/create_repo/, used by the retry button"""

    def setUp(self):
        self.rfc_to_be = RfcToBeFactory(draft__name=NAME, repository="")
        self.requester = RpcPersonFactory()
        patcher = mock.patch(
            "rpcauth.models.User.rpcperson", return_value=self.requester
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.user = get_user_model().objects.create_user(username="u")
        self.client.force_login(self.user)
        self.url = f"/api/rpc/documents/{NAME}/create_repo/"

    def test_queues_the_task_for_the_requester(self, task):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 202, response.content)
        task.delay.assert_called_once_with(self.rfc_to_be.pk, self.user.pk)

    def test_refused_when_the_document_has_a_repository(self, task):
        self.rfc_to_be.repository = FULL_NAME
        self.rfc_to_be.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400, response.content)
        task.delay.assert_not_called()

    @override_settings(GITHUB_DRAFTS_WRITE_TOKEN=None)
    def test_refused_when_not_configured(self, task):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400, response.content)
        task.delay.assert_not_called()


@override_settings(GITHUB_DRAFTS_WRITE_TOKEN="write-token")
class CreateDraftReposTaskTests(TestCase):
    """The task that creates repositories for all queued documents"""

    def setUp(self):
        self.created = RfcToBeFactory(
            draft__name="draft-a"
        )  # factory default: in_progress
        self.exists = RfcToBeFactory(draft__name="draft-b")
        self.fails = RfcToBeFactory(draft__name="draft-c")
        RfcToBeFactory(draft__name="draft-d", repository="x/draft-d")
        RfcToBeFactory(draft__name="draft-e", disposition__slug="published")
        for rfc_to_be in (self.created, self.exists, self.fails):
            rfc_to_be.repository = ""
            rfc_to_be.save()
        outcomes = {
            "draft-a": "rfc-editor-drafts/draft-a",
            "draft-b": DraftRepoExists("rfc-editor-drafts/draft-b already exists"),
            "draft-c": DraftRepoError("draft-c-00.xml is not in the IETF archive"),
        }

        def create(rfc_to_be):
            outcome = outcomes[rfc_to_be.name]
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        patcher = mock.patch("rpc.tasks.create_draft_repo", side_effect=create)
        self.create = patcher.start()
        self.addCleanup(patcher.stop)

    def test_creates_skips_and_carries_on_after_failures(self):
        with self.assertLogs("rpc.tasks", level="INFO") as logs:
            result = create_draft_repos_task()
        self.assertEqual(
            [c.args[0].name for c in self.create.call_args_list],
            ["draft-a", "draft-b", "draft-c"],
        )
        self.assertEqual(
            result, "Draft repos: 1 created, 1 skipped (already exist), 1 failed"
        )
        output = "\n".join(logs.output)
        self.assertIn("Created rfc-editor-drafts/draft-a", output)
        self.assertIn(
            "Skipped draft-b: rfc-editor-drafts/draft-b already exists", output
        )
        self.assertIn(
            "Failed draft-c: draft-c-00.xml is not in the IETF archive", output
        )

    def test_creates_no_notifications(self):
        create_draft_repos_task()
        self.assertFalse(Notification.objects.exists())

    @override_settings(GITHUB_DRAFTS_WRITE_TOKEN=None)
    def test_does_nothing_without_a_write_token(self):
        self.assertEqual(
            create_draft_repos_task(), "Draft repos not created (no write token)"
        )
        self.create.assert_not_called()
