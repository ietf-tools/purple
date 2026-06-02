# Copyright The IETF Trust 2023-2026, All Rights Reserved

from django.core.management.base import BaseCommand

from datatracker.rpcapi import get_rpcapi_client
from rpc.models import RfcToBe

STREAMS = ("irtf", "editorial")

FALLBACK_GROUPS = {
    "draft-kamei-p2p-experiments-japan": "p2prg",
    "draft-dtnrg-ltp-cbhe-registries": "dtnrg",
}


class Command(BaseCommand):
    help = "Backfill missing group for RfcToBe records with stream in "
    f"{', '.join(STREAMS)}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making any changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run — no changes will be saved"))

        qs = RfcToBe.objects.filter(
            stream__slug__in=STREAMS,
            group="",
            draft__isnull=False,
            disposition="published",
        ).select_related("draft", "stream")

        total = qs.count()
        self.stdout.write(
            f"Found {total} RfcToBe records with empty group "
            f"(streams: {', '.join(STREAMS)})"
        )

        if total == 0:
            return

        rpcapi = get_rpcapi_client()
        updated = 0
        skipped = 0

        for rfctobe in qs:
            draft = rfctobe.draft
            try:
                full_draft = rpcapi.get_draft_by_id(int(draft.datatracker_id))
            except Exception as e:
                self.stderr.write(
                    f"  SKIP {rfctobe.name} [{rfctobe.stream_id}] "
                    f"(draft_id={draft.datatracker_id}): {e}"
                )
                skipped += 1
                continue

            group = full_draft.group or ""
            if group and group.lower() != "none":
                if not dry_run:
                    rfctobe.group = group
                    rfctobe.save(update_fields=["group"])
                self.stdout.write(
                    f"  {'[DRY RUN] ' if dry_run else ''}"
                    f"{rfctobe.name} [{rfctobe.stream_id}] → group={group!r}"
                )
                updated += 1
            else:
                fallback = FALLBACK_GROUPS.get(rfctobe.name)
                if fallback:
                    if not dry_run:
                        rfctobe.group = fallback
                        rfctobe.save(update_fields=["group"])
                    self.stdout.write(
                        f"  {'[DRY RUN] ' if dry_run else ''}"
                        f"{rfctobe.name} [{rfctobe.stream_id}] → group={fallback!r} "
                        "(fallback)"
                    )
                    updated += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  {rfctobe.name} [{rfctobe.stream_id}] — no group "
                            "returned from API and no fallback defined"
                        )
                    )
                    skipped += 1

        action = "would be updated" if dry_run else "updated"
        self.stdout.write(
            f"Done: {updated} {action}, {skipped} skipped out of {total} total"
        )
