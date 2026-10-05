# Copyright The IETF Trust 2026, All Rights Reserved
"""Create a document's repository in rfc-editor-drafts when it is imported

The repo is made from rfc-editor-drafts/base-template, named after the draft (no
revision), private, with the draft's title as its description. One commit on the
Approved branch then replaces the template's README and adds the approved I-D's
txt and xml from the IETF archive, each also as a ".original" copy. The markdown
source, where there is one, is still committed by hand.

Any problem aborts with a DraftRepoError whose message is shown to the user: the
repo already existing, a file missing from the archive, or GitHub being
unreachable. Nothing is retried or partly reused.
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

DRAFTS_ORG = "rfc-editor-drafts"
TEMPLATE_REPO = "base-template"
BRANCH = "Approved"
COMMIT_MESSAGE = "approved I-D"
ARCHIVE_URL = "https://www.ietf.org/archive/id/"
REQUEST_TIMEOUT = 30  # seconds
# The template's branch may not be in the new repo yet when the create call
# returns; how long to wait for it before giving up.
BRANCH_WAIT_ATTEMPTS = 10
BRANCH_WAIT_SECONDS = 2


class DraftRepoError(Exception):
    """Creating the repo was abandoned; the message says why, for the user."""


class DraftRepoExists(DraftRepoError):
    """The repo is already there, so it was left alone."""


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
    """Path -> content of everything the first commit writes"""
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
        except UnknownObjectException:
            if attempt + 1 < BRANCH_WAIT_ATTEMPTS:
                time.sleep(BRANCH_WAIT_SECONDS)
    raise DraftRepoError(
        f"{repo.full_name} was created, but its {BRANCH} branch never appeared, "
        "so no files were committed"
    )


def _commit(repo, files: dict[str, bytes]):
    """Write all files in one commit on the branch, as base64 blobs so any bytes
    survive"""
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
    """Create and populate the document's repo; return its "owner/name"

    Raises DraftRepoError, with a message for the user, if it can't.
    """
    name = rfc_to_be.name
    # Before touching GitHub, so a missing file leaves nothing behind.
    files = _repo_files(rfc_to_be)
    try:
        github = Github(auth=GithubAuthToken(settings.GITHUB_DRAFTS_WRITE_TOKEN))
        org = github.get_organization(DRAFTS_ORG)
        try:
            org.get_repo(name)
        except UnknownObjectException:
            pass
        else:
            raise DraftRepoExists(f"{DRAFTS_ORG}/{name} already exists")
        repo = org.create_repo_from_template(
            name,
            github.get_repo(f"{DRAFTS_ORG}/{TEMPLATE_REPO}"),
            description=rfc_to_be.title,
            private=True,
        )
        _commit(repo, files)
    except GithubException as err:
        logger.exception("GitHub error creating the repo for %s", name)
        raise DraftRepoError(
            f"GitHub failed while creating {DRAFTS_ORG}/{name} ({err.status})"
        ) from err
    except requests.RequestException as err:
        logger.exception("Could not reach GitHub to create the repo for %s", name)
        raise DraftRepoError(f"Could not reach GitHub to create {name}") from err
    rfc_to_be.repository = repo.full_name
    rfc_to_be.save(update_fields=["repository"])
    return repo.full_name
