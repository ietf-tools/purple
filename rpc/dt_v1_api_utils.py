# Copyright The IETF Trust 2024, All Rights Reserved

from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.cache import cache


class DatatrackerFetchFailure(Exception):
    pass


class NoSuchSlug(Exception):
    pass


REQUEST_TIMEOUT = 10  # seconds


def _get_cf_headers(url: str) -> dict:
    """Return CF Access service token headers if the URL host is configured for it."""
    if getattr(settings, "CF_SERVICE_TOKEN_HOSTS", None) is not None:
        if urlparse(url).hostname in settings.CF_SERVICE_TOKEN_HOSTS:
            return {
                "CF-Access-Client-Id": settings.CF_SERVICE_TOKEN_ID,
                "CF-Access-Client-Secret": settings.CF_SERVICE_TOKEN_SECRET,
            }
    return {}


def datatracker_name(namemodel: str, slug: str) -> tuple[str, str, str]:
    cache_key = f"dt_name:{namemodel}:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = f"{settings.DATATRACKER_API_V1_BASE}/name/{namemodel}"
    api_response = datatracker_api_get(url, params={"fmt": "json", "slug": slug})
    hits = api_response["meta"]["total_count"]
    if hits > 1:
        raise DatatrackerFetchFailure
    elif hits == 0:
        raise NoSuchSlug
    else:
        obj = api_response["objects"][0]
        result = (obj["slug"], obj["name"], obj["desc"])
        cache.set(cache_key, result)
        return result


def datatracker_stdlevelname(slug: str) -> tuple[str, str, str]:
    return datatracker_name("stdlevelname", slug)


def datatracker_streamname(slug: str) -> tuple[str, str, str]:
    return datatracker_name("streamname", slug)


def _fetch_group_object(acronym: str) -> dict | None:
    """Fetch the group object from the datatracker API for a given acronym."""
    cache_key = f"dt_group_object:{acronym}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    url = f"{settings.DATATRACKER_API_V1_BASE}/group/group/"
    api_response = datatracker_api_get(url, params={"acronym": acronym, "fmt": "json"})
    objects = api_response.get("objects", [])
    result = objects[0] if objects else None
    if result is not None:
        cache.set(cache_key, result)
    return result


def datatracker_group_list_email(acronym: str) -> str | None:
    """Return the mailing list email for a group, or None if not found."""
    obj = _fetch_group_object(acronym)
    return obj.get("list_email") or None if obj else None


def datatracker_group_name(acronym: str) -> str | None:
    """Return the full name of a group, or None if not found."""
    obj = _fetch_group_object(acronym)
    return obj.get("name") or None if obj else None


@dataclass
class GroupChair:
    datatracker_person_id: int | None
    email: str
    name: str


def datatracker_group_chair(group_acronym: str) -> "GroupChair | None":
    """Return datatracker_person_id, email and name of the chair of a group, or None
    if not found."""
    url = f"{settings.DATATRACKER_API_V1_BASE}/group/role/"
    try:
        api_response = datatracker_api_get(
            url,
            params={
                "name__slug": "chair",
                "group__acronym": group_acronym,
                "fmt": "json",
            },
        )
    except DatatrackerFetchFailure:
        return None
    objects = api_response.get("objects", [])
    if not objects:
        return None
    role = objects[0]
    email = role.get("email", "")
    person_url = role.get("person", "")
    name = ""
    if person_url:
        try:
            person_url_full = f"{settings.DATATRACKER_BASE}{person_url}"
            person_response = requests.get(
                person_url_full,
                params={"format": "json"},
                allow_redirects=True,
                timeout=REQUEST_TIMEOUT,
                headers=_get_cf_headers(person_url_full),
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
    return GroupChair(datatracker_person_id=person_id_int, email=email, name=name)


def datatracker_docevents(type: str, limit: int = 1000):
    """Yield pages of docevent objects from the datatracker v1 API.

    Use with itertools.chain.from_iterable() to iterate over all events.
    Each event is a dict with at least 'doc' and 'time' keys.
    """
    url = (
        f"{settings.DATATRACKER_API_V1_BASE}/doc/docevent/"
        f"?fmt=json&type={type}&limit={limit}"
    )
    while url:
        api_response = datatracker_api_get(url)
        yield api_response.get("objects", [])
        next_url = api_response.get("meta", {}).get("next")
        url = f"{settings.DATATRACKER_BASE}{next_url}" if next_url else None


def datatracker_api_get(
    url: str, params: dict | None = None, timeout: int = REQUEST_TIMEOUT
) -> object:
    try:
        response = requests.get(
            url,
            params=params,
            allow_redirects=True,
            timeout=timeout,
            headers=_get_cf_headers(url),
        )
    except requests.exceptions.ConnectionError as err:
        raise DatatrackerFetchFailure from err
    if not response.ok:
        raise DatatrackerFetchFailure
    api_response = response.json()
    if "meta" not in api_response:
        raise DatatrackerFetchFailure
    return api_response
