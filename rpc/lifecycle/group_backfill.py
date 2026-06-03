# Copyright The IETF Trust 2026, All Rights Reserved

import logging

logger = logging.getLogger(__name__)

STREAMS = ("irtf", "editorial")

FALLBACK_GROUPS = {
    "draft-kamei-p2p-experiments-japan": "p2prg",
    "draft-dtnrg-ltp-cbhe-registries": "dtnrg",
}


def backfill_missing_groups(dry_run: bool = False) -> tuple[int, int, int]:
    """Backfill the group field for RfcToBe records with stream in STREAMS where it is "
    empty.

    Returns (total, updated, skipped).
    """
    from datatracker.rpcapi import get_rpcapi_client
    from rpc.models import RfcToBe

    qs = RfcToBe.objects.filter(
        stream__slug__in=STREAMS,
        group="",
        draft__isnull=False,
        disposition="published",
    ).select_related("draft", "stream")

    total = qs.count()
    logger.info(
        "backfill_missing_groups: found %d records with empty group (streams: %s)",
        total,
        ", ".join(STREAMS),
    )

    if total == 0:
        return total, 0, 0

    rpcapi = get_rpcapi_client()
    updated = 0
    skipped = 0

    for rfctobe in qs:
        draft = rfctobe.draft
        try:
            full_draft = rpcapi.get_draft_by_id(int(draft.datatracker_id))
        except Exception as e:
            logger.warning(
                "backfill_missing_groups: SKIP %s (draft_id=%s): %s",
                rfctobe.name,
                draft.datatracker_id,
                e,
            )
            skipped += 1
            continue

        group = full_draft.group or ""
        if group and group.lower() != "none":
            if not dry_run:
                rfctobe.group = group
                rfctobe.save(update_fields=["group"])
            prefix = "[DRY RUN] " if dry_run else ""
            logger.info(
                "backfill_missing_groups: %s%s [%s] → group=%r",
                prefix,
                rfctobe.name,
                rfctobe.stream_id,
                group,
            )
            updated += 1
        else:
            fallback = FALLBACK_GROUPS.get(rfctobe.name)
            if fallback:
                if not dry_run:
                    rfctobe.group = fallback
                    rfctobe.save(update_fields=["group"])
                prefix = "[DRY RUN] " if dry_run else ""
                logger.info(
                    "backfill_missing_groups: %s%s [%s] → group=%r (fallback)",
                    prefix,
                    rfctobe.name,
                    rfctobe.stream_id,
                    fallback,
                )
                updated += 1
            else:
                logger.warning(
                    "backfill_missing_groups: %s [%s] — no group from API and no "
                    "fallback defined",
                    rfctobe.name,
                    rfctobe.stream_id,
                )
                skipped += 1

    return total, updated, skipped
