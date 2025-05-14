# Copyright The IETF Trust 2023-2024, All Rights Reserved
from django.db.models import Max

from .models import DumpInfo, RfcToBe, UnusableRfcNumber


class VersionInfo:
    """Application version information model"""

    version = "version-access-not-yet-implemented"

    def __init__(self):
        # If we have a DumpInfo, populate the dump_timestamp property
        dumpinfo = DumpInfo.objects.order_by("-timestamp").first()
        if dumpinfo is not None:
            self.dump_timestamp = dumpinfo.timestamp


def next_rfc_number(count=1) -> list[int]:
    """Find the next count contiguous available RFC numbers"""
    # In the worst-case, we can always use (n + 1) to (n + count) where n is the last
    # unavailable number.
    last_unavailable_number = max(
        (
            UnusableRfcNumber.objects.aggregate(Max("number"))["number__max"] or 0,
            RfcToBe.objects.aggregate(Max("rfc_number"))["rfc_number__max"] or 0,
            # todo get last RFC number from datatracker
        )
    )
    # todo consider holes in the unavailable number sequence
    return list(range(last_unavailable_number + 1, last_unavailable_number + 1 + count))
