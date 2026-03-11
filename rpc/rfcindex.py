# Copyright The IETF Trust 2026, All Rights Reserved
import json
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.files.storage import storages
from django.db.models import QuerySet

from rpc.models import RfcToBe, UnusableRfcNumber


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
    bucket_path = Path(getattr(settings, "RFCINDEX_SUPPORT_PATH", ""))
    for filename, contents in json_data.items():
        red_bucket.save(bucket_path / filename, StringIO(contents))
