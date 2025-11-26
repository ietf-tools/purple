# Copyright The IETF Trust 2025, All Rights Reserved
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings


def build_datatracker_url(url):
    """Build an absolute datatracker URL

    Takes an absolute or relative URL and constructs an absolute URL on the correct
    datatracker base URL. For a relative URL, this is equivalent to urljoin. For an
    absolute URL, it ensures we don't accidentally refer to the production datatracker
    when running in a dev or staging environment.
    """
    baseparts = urlsplit(settings.DATATRACKER_BASE)
    urlparts = urlsplit(url)._replace(
        scheme=baseparts.scheme,
        netloc=baseparts.netloc,
    )
    return urlunsplit(urlparts)
