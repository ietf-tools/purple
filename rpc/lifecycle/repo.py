# Copyright The IETF Trust 2025, All Rights Reserved
"""Document repository interfaces"""

import json
import logging
from pathlib import Path, PurePath

import jsonschema
import requests
from django.conf import settings
from django.core.files.base import File
from github import Github, GithubException
from github.Auth import Auth as GithubAuth
from github.Auth import Token as GithubAuthToken
from requests import HTTPError

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30  # seconds


class RepositoryFile(File):
    """Base class for RepositoryFiles

    Chunked access only.
    """

    def open(self, *args, **kwargs):
        raise ValueError("File cannot be opened. Use chunks or iterate instead")

    def close(self):
        pass  # file is never open


class GithubRepositoryFile(RepositoryFile):
    def __init__(self, name, download_url, size):
        super().__init__(file=None, name=name)
        self.size = size
        self._download_url = download_url
        self._downloaded = False  # can only download once

    def _get(self):
        if self._downloaded:
            raise ValueError("File can only be downloaded once")
        self._downloaded = True
        logger.debug("Making request: GET %s", self._download_url)
        response = requests.get(
            url=self._download_url,
            allow_redirects=True,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response

    def chunks(self, chunk_size=None):
        try:
            response = self._get()
        except HTTPError as err:
            if err.response.status_code // 100 == 5:  # 5xx
                raise TemporaryRepositoryError(
                    f"Server error ({err.response.status_code}) "
                    f"downloading {self.name} from Github"
                ) from err
            raise RepositoryError(f"Error downloading {self.name} from Github") from err
        try:
            yield from response.iter_content(chunk_size or self.DEFAULT_CHUNK_SIZE)
        except Exception as err:
            # initial request succeeded, so failure to read a chunk is temporary
            raise TemporaryRepositoryError(
                f"Error retrieving chunk of {self.name}"
            ) from err


class Repository:
    """Base class for Repository"""

    MANIFEST_PATH = "manifest.json"  # path in repo
    MANIFEST_SCHEMA = "pubmanifest.schema.json"  # file relative to this script

    def validate_manifest(self, manifest):
        manifest_path = settings.SCHEMA_ROOT / self.MANIFEST_SCHEMA
        with manifest_path.open() as schema_file:
            jsonschema.validate(manifest, json.load(schema_file))

    def get_file(self, path: PurePath | str) -> RepositoryFile:
        raise NotImplementedError


class GithubRepository(Repository):
    """Github repository

    Raises a RepositoryError if something goes wrong indicating a problem with
    the repository contents. Raises GithubException if there is an issue with
    Github itself.
    """

    def __init__(self, repo_id: str, auth: GithubAuth | None = None):
        if auth is None:
            auth_token = getattr(settings, "GITHUB_AUTH_TOKEN", None)
            if auth_token is not None:
                auth = GithubAuthToken(auth_token)
        self.gh = Github(auth=auth)
        self.repo = self.gh.get_repo(repo_id)

    def get_manifest(self):
        logger.debug("Retrieving manifest from %s", self.repo.name)
        try:
            contents = self.repo.get_contents(self.MANIFEST_PATH)
        except GithubException as err:
            if err.status // 100 == 5:  # 5xx
                raise TemporaryRepositoryError from err
            raise RepositoryError from err  # convert to RepositoryError otherwise
        if contents.type != "file":
            raise RepositoryError("Manifest is not a file (type is %s)", contents.type)
        try:
            manifest = json.loads(contents.decoded_content)
            self.validate_manifest(manifest)
        except Exception as err:
            raise RepositoryError from err
        return manifest

    def get_file(self, path: PurePath | str) -> GithubRepositoryFile:
        # We can't use decoded_content because the file might be too large (> 1 MB).
        # Instead, use GithubRepositoryFile so it can be chunked via download_url.
        path = str(path)
        contents = self.repo.get_contents(path)
        if contents.type != "file":
            raise RepositoryError("Path is not a file (type is %s)", contents.type)
        return GithubRepositoryFile(
            name=contents.name,
            download_url=contents.download_url,
            size=contents.size,
        )


class RepositoryError(Exception):
    """Base class for repository exceptions"""


class TemporaryRepositoryError(RepositoryError):
    """Repository exception that is likely temporary and worth retrying"""
