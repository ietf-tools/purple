# Copyright The IETF Trust 2026, All Rights Reserved
import datetime
import json
import logging
from io import StringIO
from pathlib import Path

import rpcapi_client
from django.conf import settings
from django.core.files.storage import storages
from django.db.models import Q, QuerySet
from django.utils import timezone

from datatracker.rpcapi import with_rpcapi
from rpc.models import DirtyBits, RfcToBe, UnusableRfcNumber

logger = logging.getLogger(__name__)


def generate_unusable_rfc_numbers_json():
    return json.dumps(
        [
            {"number": unusable.number, "comment": unusable.comment}
            for unusable in UnusableRfcNumber.objects.all()
        ]
    )


def generate_april_first_rfc_json():
    april_first_rfcs = RfcToBe.objects.filter(
        is_april_first_rfc=True,
        rfc_number__isnull=False,
        disposition__slug="published",
    )
    return json.dumps([rfc_to_be.rfc_number for rfc_to_be in april_first_rfcs])


def generate_publication_std_level_json():
    published_rfcs: QuerySet[RfcToBe] = RfcToBe.objects.filter(
        rfc_number__isnull=False,
        disposition__slug="published",
    )
    return json.dumps(
        [
            {
                "number": rfc_to_be.rfc_number,
                "publication_std_level": rfc_to_be.publication_std_level_id,
            }
            for rfc_to_be in published_rfcs
        ]
    )


def create_rfc_index_support_blobs():
    """Create JSON blobs for rfc-index generation and store in red bucket"""
    red_bucket = storages["red_bucket"]
    json_data = {
        "unusable-rfc-numbers.json": generate_unusable_rfc_numbers_json(),
        "april-first-rfc-numbers.json": generate_april_first_rfc_json(),
        "publication-std-levels.json": generate_publication_std_level_json(),
    }
    bucket_path = Path(getattr(settings, "RFCINDEX_SUPPORT_BLOB_PATH", ""))
    for filename, contents in json_data.items():
        red_bucket.save(bucket_path / filename, StringIO(contents))


@with_rpcapi
def refresh_rfc_index(*, rpcapi: rpcapi_client.PurpleApi):
    """Refresh the RFC index

    Generates necessary support files and asks datatracker to generate the new
    indexes.
    """
    create_rfc_index_support_blobs()
    rpcapi.refresh_rfc_index()


## DirtyBits management for the RFC index

RFCINDEX_SLUG = DirtyBits.Slugs.RFCINDEX


def mark_rfcindex_as_dirty():
    _, created = DirtyBits.objects.update_or_create(
        slug=RFCINDEX_SLUG, defaults={"dirty_time": timezone.now()}
    )
    if created:
        logger.debug("Created DirtyBits(slug='%(slug)s')", {"slug": RFCINDEX_SLUG})


def mark_rfcindex_as_processed(when: datetime.datetime):
    n_updated = DirtyBits.objects.filter(
        Q(processed_time__isnull=True) | Q(processed_time__lt=when),
        slug=RFCINDEX_SLUG,
    ).update(processed_time=when)
    if n_updated > 0:
        logger.debug(
            "processed_time is now %(processed_time)s",
            {"processed_time": when.isoformat()},
        )
    else:
        logger.debug("processed_time not updated, no matching record found")


def rfcindex_is_dirty():
    """Does the rfc index need to be updated?"""
    dirty_work, created = DirtyBits.objects.get_or_create(
        slug=RFCINDEX_SLUG, defaults={"dirty_time": timezone.now()}
    )
    if created:
        logger.debug("Created DirtyBits(slug='%(slug)s')", {"slug": RFCINDEX_SLUG})
    logger.debug(
        "DirtyBits(slug='%(slug)s'): dirty_time=%(dirty_time)s "
        "processed_time=%(processed_time)s",
        {
            "slug": RFCINDEX_SLUG,
            "dirty_time": dirty_work.dirty_time.isoformat(),
            "processed_time": dirty_work.processed_time.isoformat()
            if dirty_work.processed_time is not None
            else "never",
        },
    )
    return (
        dirty_work.processed_time is None
        or dirty_work.dirty_time >= dirty_work.processed_time
    )
