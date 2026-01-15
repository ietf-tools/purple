# Copyright The IETF Trust 2025, All Rights Reserved
"""Document repository interfaces"""

import datetime
import json
import logging
import xml.etree.ElementTree as ET
from pathlib import PurePath

import jsonschema
import requests
from django.conf import settings
from django.core.files.base import File
from github import Github, GithubException
from github.Auth import Auth as GithubAuth
from github.Auth import Token as GithubAuthToken
from requests import HTTPError
from django.db import transaction
from rpc.models import (
    RpcRelatedDocument,
    DocRelationshipName,
    RfcToBe,
    SubseriesMember,
    SubseriesTypeName,
)


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

    def get_head_sha(self) -> str:
        """Get the SHA of the head commit of the default branch."""
        try:
            commits = self.repo.get_commits()
            head_commit = commits[0]
            return head_commit.sha
        except GithubException as err:
            if err.status // 100 == 5:  # 5xx
                raise TemporaryRepositoryError from err
            raise RepositoryError from err


class RepositoryError(Exception):
    """Base class for repository exceptions"""


class TemporaryRepositoryError(RepositoryError):
    """Repository exception that is likely temporary and worth retrying"""


class Metadata:
    """Base class for metadata extraction"""

    @staticmethod
    def parse_rfc_xml(xml_string):
        root = ET.fromstring(xml_string)
        ns = {}

        front = root.find("front", ns)
        if front is None:
            return None

        title_elem = front.find("title", ns)
        title = title_elem.text.strip() if title_elem is not None else ""

        abstract_elem = front.find("abstract", ns)
        abstract_text = ""
        if abstract_elem is not None:
            abstract_text = " ".join(
                t.text.strip() for t in abstract_elem.findall("t", ns) if t.text
            )

        authors = []
        for author in front.findall("author", ns):
            author_dict = dict(author.attrib)
            org_elem = author.find("organization", ns)
            if org_elem is not None and org_elem.text:
                author_dict["organization"] = org_elem.text.strip()
            if author_dict:
                authors.append(author_dict)

        obsoletes_str = root.attrib.get("obsoletes", "")
        obsoletes = (
            [s.strip() for s in obsoletes_str.split(",") if s.strip()]
            if obsoletes_str
            else []
        )

        updates_str = root.attrib.get("updates", "")
        updates = (
            [s.strip() for s in updates_str.split(",") if s.strip()]
            if updates_str
            else []
        )

        date_elem = front.find("date", ns)
        date = None
        if date_elem is not None:
            date = {
                "month": date_elem.attrib.get("month"),
                "day": date_elem.attrib.get("day"),
                "year": date_elem.attrib.get("year"),
            }

        subseries = []
        for series_info in root.findall("seriesInfo", ns):
            name = series_info.attrib.get("name")
            if name in ("BCP", "FYI", "STD"):
                value = series_info.attrib.get("value")
                if name and value:
                    subseries.append({"name": name, "value": value})

        return {
            "title": title,
            "abstract": abstract_text,
            "authors": authors,
            "obsoletes": obsoletes,
            "updates": updates,
            "publication_date": date,
            "subseries": subseries,
        }

    @staticmethod
    def update_metadata(rfctobe, metadata):
        """Update the draft title from metadata dictionary"""

        updated_fields = {}

        with transaction.atomic():
            # title
            new_title = metadata.get("title")
            draft = rfctobe.draft
            if not new_title:
                raise ValueError("No title in metadata")
            draft.title = new_title
            draft.save(update_fields=["title"])
            updated_fields["title"] = new_title

            # obsoletes and updates
            # Delete existing obsoletes and updates relationships
            RpcRelatedDocument.objects.filter(
                source=rfctobe, relationship__slug__in=["obs", "updates"]
            ).delete()

            # Create new obsoletes relationships
            obsoletes = metadata.get("obsoletes", [])
            relationship = DocRelationshipName.objects.get(slug="obs")
            for rfc_num in obsoletes:
                try:
                    target_rfctobe = RfcToBe.objects.get(rfc_number=rfc_num)
                    RpcRelatedDocument.objects.create(
                        source=rfctobe,
                        relationship=relationship,
                        target_rfctobe=target_rfctobe,
                    )
                except RfcToBe.DoesNotExist:
                    logger.warning(
                        f"RFC {rfc_num} not found for obsoletes relationship"
                    )

            # Create new updates relationships
            updates = metadata.get("updates", [])
            relationship = DocRelationshipName.objects.get(slug="updates")
            for rfc_num in updates:
                try:
                    target_rfctobe = RfcToBe.objects.get(rfc_number=rfc_num)
                    RpcRelatedDocument.objects.create(
                        source=rfctobe,
                        relationship=relationship,
                        target_rfctobe=target_rfctobe,
                    )
                except RfcToBe.DoesNotExist:
                    logger.warning(f"RFC {rfc_num} not found for updates relationship")

            updated_fields["obsoletes"] = obsoletes
            updated_fields["updates"] = updates

            # abstract
            # todo

            # authors
            # todo: implement author updates of affiliation, order and is_editor

            # publication status
            # todo

            # publication date
            pub_date = metadata.get("publication_date")
            if pub_date:
                year = int(pub_date.get("year"))
                month_str = pub_date.get("month")
                day = int(pub_date.get("day", 1))

                if not year or not month_str or not day:
                    raise ValueError("Incomplete publication date in metadata")

                # Convert month name to month number
                month = datetime.datetime.strptime(month_str, "%B").month

                rfctobe.published_at = datetime.datetime(year, month, day, 12, 0, 0)
                rfctobe.save(
                    update_fields=[
                        "published_at",
                    ]
                )
                updated_fields["published_at"] = rfctobe.published_at

            # subseries
            # Delete all existing subseries memberships
            SubseriesMember.objects.filter(rfc_to_be=rfctobe).delete()

            # Create new subseries memberships
            subseries = metadata.get("subseries", [])
            for subseries_item in subseries:
                # subseries_item is like {"name": "BCP", "value": "38"}
                type_slug = subseries_item.get("name", "").lower()
                number = subseries_item.get("value")

                if type_slug and number:
                    try:
                        subseries_type = SubseriesTypeName.objects.get(slug=type_slug)
                        SubseriesMember.objects.create(
                            rfc_to_be=rfctobe,
                            type=subseries_type,
                            number=int(number),
                        )
                    except SubseriesTypeName.DoesNotExist:
                        logger.warning(f"Subseries type {type_slug} not found")
                    except ValueError:
                        logger.warning(f"Invalid subseries number: {number}")

            updated_fields["subseries"] = subseries

        return updated_fields
