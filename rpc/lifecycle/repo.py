# Copyright The IETF Trust 2025, All Rights Reserved
"""Document repository interfaces"""
import os
from typing import Iterator

import requests
from django.conf import settings
from django.core.files.base import File
from github import Github
from github.Auth import Auth as GithubAuth, Token as GithubAuthToken
from pathlib import PurePath

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
        response = requests.get(
            url=self._download_url,
            allow_redirects=True,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response

    def chunks(self, chunk_size=None):
        for chunk in self._get().iter_content(chunk_size or self.DEFAULT_CHUNK_SIZE):
            yield chunk


class Repository:
    """Base class for Repository"""

    def directory_contents(self, directory: PurePath | str) -> Iterator[RepositoryFile]:
        raise NotImplemented


class GithubRepository(Repository):
    """Github repository"""

    def __init__(self, repo_id: str, ref: str | None = None, auth: GithubAuth | None = None):
        if auth is None:
            auth_token = getattr(settings, "GITHUB_AUTH_TOKEN", None)
            if auth_token is not None:
                auth = GithubAuthToken(auth_token)
        self.gh = Github(auth=auth)
        self.repo = self.gh.get_repo(repo_id)
        self.ref = ref  # pin to a particular git ref

    def directory_contents(self, directory: PurePath | str):
        """Iterate files matching glob pattern"""
        directory = str(directory)  # convert a Path to a directory
        contents = (
            self.repo.get_contents(directory)
            if self.ref is None
            else self.repo.get_contents(directory, self.ref)
        )
        for rf in contents:
            if rf.type == "file":
                yield GithubRepositoryFile(
                    name=rf.name,
                    download_url=rf.download_url,
                    size=rf.size,
                )
