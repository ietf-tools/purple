# Copyright The IETF Trust 2024, All Rights Reserved

import requests
from django.conf import settings


class DatatrackerFetchFailure(Exception):
    pass


class NoSuchSlug(Exception):
    pass


def datatracker_name(namemodel: str, slug: str) -> tuple[str, str, str]:
    try:
        response = requests.get(
            f"{settings.DATATRACKER_API_V1_BASE}/name/{namemodel}?fmt=json&slug={slug}"
        )
    except requests.exceptions.ConnectionError as err:
        raise DatatrackerFetchFailure from err
    if not response.ok:
        raise DatatrackerFetchFailure
    api_response = response.json()
    if "meta" not in api_response:
        raise DatatrackerFetchFailure
    hits = api_response["meta"]["total_count"]
    if hits > 1:
        raise DatatrackerFetchFailure
    elif hits == 0:
        raise NoSuchSlug
    else:
        obj = api_response["objects"][0]
        return (obj["slug"], obj["name"], obj["desc"])


def datatracker_stdlevelname(slug: str) -> tuple[str, str, str]:
    return datatracker_name("stdlevelname", slug)


def datatracker_streamname(slug: str) -> tuple[str, str, str]:
    return datatracker_name("streamname", slug)


def datatracker_group_list_email(acronym: str) -> str | None:
    """Return the mailing list email for a group, or None if not found."""
    try:
        response = requests.get(
            f"{settings.DATATRACKER_API_V1_BASE}/group/group/",
            params={"acronym": acronym, "fmt": "json"},
        )
    except requests.exceptions.ConnectionError:
        return None
    if not response.ok:
        return None
    api_response = response.json()
    objects = api_response.get("objects", [])
    if not objects:
        return None
    return objects[0].get("list_email") or None
