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


from dataclasses import dataclass


@dataclass
class GroupChair:
    id: int
    email: str
    name: str


def datatracker_group_chair(group_acronym: str) -> "GroupChair | None":
    """Return id, email and name of the chair of a group, or None if not found."""
    try:
        response = requests.get(
            f"{settings.DATATRACKER_API_V1_BASE}/group/role/",
            params={"name__slug": "chair", "group__acronym": group_acronym, "format": "json"},
        )
    except requests.exceptions.ConnectionError:
        return None
    if not response.ok:
        return None
    objects = response.json().get("objects", [])
    if not objects:
        return None
    role = objects[0]
    email = role.get("email", {}).get("address") or ""
    person_url = role.get("person", "")
    name = ""
    if person_url:
        try:
            person_response = requests.get(
                f"{settings.DATATRACKER_BASE}{person_url}",
                params={"format": "json"},
            )
            if person_response.ok:
                name = person_response.json().get("plain_name") or ""
        except requests.exceptions.ConnectionError:
            pass
    person_id = role.get("person", "").rstrip("/").rsplit("/", 1)[-1]
    try:
        person_id_int = int(person_id)
    except (ValueError, TypeError):
        person_id_int = 0
    return GroupChair(id=person_id_int, email=email, name=name)
