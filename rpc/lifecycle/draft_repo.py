# Copyright The IETF Trust 2026, All Rights Reserved
"""Create a document's repository in the drafts organization on import

The repository is created from the organization's base-template (organization:
GITHUB_DRAFTS_ORG), is private, is named after the draft without its revision, and
uses the draft title as its description. A single commit on the Approved branch
replaces the README and adds the approved I-D's txt and xml from the IETF archive,
each together with a ".original" copy. Markdown sources are committed manually.

Every failure raises DraftRepoError with a message intended for the user, for
example an existing repository, a file missing from the archive, or GitHub being
unavailable. Failed attempts are not retried.
"""

import base64
import logging
import time

import requests
from django.conf import settings
from github import Github, GithubException, UnknownObjectException
from github.Auth import Token as GithubAuthToken
from github.InputGitTreeElement import InputGitTreeElement

from rpc.models import RfcToBe

logger = logging.getLogger(__name__)

TEMPLATE_REPO = "base-template"
BRANCH = "Approved"
COMMIT_MESSAGE = "approved I-D"
ARCHIVE_URL = "https://www.ietf.org/archive/id/"
REQUEST_TIMEOUT = 30  # seconds
# GitHub populates a repository created from a template asynchronously. Until it
# has done so, requests for the branch return 409 ("Git Repository is empty") or
# 404.
BRANCH_WAIT_ATTEMPTS = 10
BRANCH_WAIT_SECONDS = 2
_NOT_READY_STATUSES = (404, 409)


class DraftRepoError(Exception):
    """Repository creation stopped; the message is shown to the user."""


class DraftRepoExists(DraftRepoError):
    """The repository already exists and was not modified."""


def is_enabled() -> bool:
    return bool(settings.GITHUB_DRAFTS_WRITE_TOKEN)


def _download(filename: str) -> bytes:
    url = f"{ARCHIVE_URL}{filename}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as err:
        raise DraftRepoError(
            f"Could not reach the IETF archive for {filename}"
        ) from err
    if response.status_code == 404:
        raise DraftRepoError(f"{filename} is not in the IETF archive")
    if not response.ok:
        raise DraftRepoError(
            f"The IETF archive answered {response.status_code} for {filename}"
        )
    return response.content


def _repo_files(rfc_to_be: RfcToBe) -> dict[str, bytes]:
    """Files for the initial commit, as path -> content"""
    name = rfc_to_be.name
    if not rfc_to_be.rev:
        raise DraftRepoError(f"{name} has no revision, so its files can't be found")
    versioned = f"{name}-{rfc_to_be.rev}"
    txt = _download(f"{versioned}.txt")
    xml = _download(f"{versioned}.xml")
    return {
        "README.md": f"# {name}\n".encode(),
        f"{versioned}.txt": txt,
        f"{versioned}.original": txt,
        f"{versioned}.xml": xml,
        f"{versioned}.original.xml": xml,
    }


def _wait_for_branch(repo):
    for attempt in range(BRANCH_WAIT_ATTEMPTS):
        try:
            return repo.get_git_ref(f"heads/{BRANCH}")
        except GithubException as err:
            if err.status not in _NOT_READY_STATUSES:
                raise
            if attempt + 1 < BRANCH_WAIT_ATTEMPTS:
                time.sleep(BRANCH_WAIT_SECONDS)
    raise DraftRepoError(
        f"{repo.full_name} was created, but its {BRANCH} branch never appeared, "
        "so no files were committed"
    )


def _commit(repo, files: dict[str, bytes]):
    """Write all files in one commit on the branch. Blobs are sent base64-encoded."""
    ref = _wait_for_branch(repo)
    parent = repo.get_git_commit(ref.object.sha)
    tree = repo.create_git_tree(
        [
            InputGitTreeElement(
                path,
                "100644",
                "blob",
                sha=repo.create_git_blob(
                    base64.b64encode(content).decode(), "base64"
                ).sha,
            )
            for path, content in files.items()
        ],
        parent.tree,
    )
    commit = repo.create_git_commit(COMMIT_MESSAGE, tree, [parent])
    ref.edit(commit.sha)


def create_draft_repo(rfc_to_be: RfcToBe) -> str:
    """Create and populate the document's repository and return its "owner/name".

    Raises DraftRepoError, with a message for the user, if this is not possible.
    """
    name = rfc_to_be.name
    drafts_org = settings.GITHUB_DRAFTS_ORG
    # Download first, so that a missing file does not leave an empty repository.
    files = _repo_files(rfc_to_be)
    try:
        github = Github(auth=GithubAuthToken(settings.GITHUB_DRAFTS_WRITE_TOKEN))
        org = github.get_organization(drafts_org)
        try:
            org.get_repo(name)
        except UnknownObjectException:
            pass
        else:
            raise DraftRepoExists(f"{drafts_org}/{name} already exists")
        repo = org.create_repo_from_template(
            name,
            github.get_repo(f"{drafts_org}/{TEMPLATE_REPO}"),
            description=rfc_to_be.title,
            private=True,
        )
        _commit(repo, files)
    except GithubException as err:
        logger.exception("GitHub error creating the repo for %s", name)
        raise DraftRepoError(
            f"GitHub failed while creating {drafts_org}/{name} ({err.status})"
        ) from err
    except requests.RequestException as err:
        logger.exception("Could not reach GitHub to create the repo for %s", name)
        raise DraftRepoError(f"Could not reach GitHub to create {name}") from err
    rfc_to_be.repository = repo.full_name
    rfc_to_be.save(update_fields=["repository"])
    return repo.full_name
