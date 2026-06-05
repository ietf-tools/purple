# Copyright The IETF Trust 2026, All Rights Reserved

import datetime
import logging

logger = logging.getLogger(__name__)

# (draft_name, start_date, assignment_pk) — assignment_pk is the PK of the first
# final_review_editor Assignment for that draft; start_date is when it was created
FINAL_REVIEW_START_DATES = [
    ("draft-ietf-tls-rfc8446bis", "2025-12-15", 154),
    ("draft-ietf-tls-keylogfile", "2025-12-16", 114),
    ("draft-ietf-tls-tls12-frozen", "2026-01-05", 120),
    ("draft-ietf-uta-require-tls13", "2026-01-06", 126),
    ("draft-ietf-stir-servprovider-oob", "2025-10-21", 144),
    ("draft-ietf-pce-pceps-tls13", "2026-01-16", 30),
    ("draft-ietf-netconf-over-tls13", "2026-01-16", 36),
    ("draft-ietf-lamps-rfc5019bis", "2026-01-16", 88),
    ("draft-ietf-pce-sid-algo", "2026-02-19", 193),
    ("draft-ietf-cose-merkle-tree-proofs", "2026-03-06", 170),
    ("draft-ietf-scitt-architecture", "2026-03-06", 182),
    ("draft-ietf-tls-hybrid-design", "2026-04-03", 175),
    ("draft-ietf-pquip-hybrid-signature-spectrums", "2026-04-03", 3),
    ("draft-ietf-pquip-pqc-engineers", "2026-04-27", 137),
    ("draft-ietf-emu-bootstrapped-tls", "2026-04-27", 188),
    ("draft-ietf-stir-rfc4916-update", "2026-05-01", 213),
    ("draft-ietf-bmwg-mlrsearch", "2026-05-13", 218),
    ("draft-ietf-tls-8773bis", "2026-04-06", 162),
    ("draft-ietf-bier-oam-requirements", "2026-05-04", 51),
    ("draft-ietf-dnsop-cds-consistency", "2026-05-06", 256),
    ("draft-ietf-opsawg-prefix-lengths", "2026-05-06", 262),
    ("draft-ietf-bfd-stability", "2026-05-07", 234),
    ("draft-ietf-mailmaint-messageflag-mailboxattribute", "2026-05-07", 268),
    ("draft-ietf-openpgp-pqc", "2026-05-08", 200),
    ("draft-ietf-sidrops-manifest-numbers", "2026-05-08", 311),
    ("draft-ietf-calext-jscontact-uid", "2026-05-12", 305),
    ("draft-ietf-netconf-udp-client-server", "2026-05-13", 275),
    ("draft-ietf-bfd-optimizing-authentication", "2026-05-19", 241),
    ("draft-ietf-sshm-ssh-agent", "2026-05-14", 373),
    ("draft-ietf-avtcore-rtp-haptics", "2026-05-18", 317),
]


def backfill_final_review_history(dry_run: bool = False) -> tuple[int, int]:
    """Backfill missing history creation entries for final_review_editor assignments.

    Returns (added, skipped).
    """
    from rpc.models import Assignment

    HistoricalAssignment = Assignment.history.model
    added = 0
    skipped = 0

    for draft_name, date_str, assignment_pk in FINAL_REVIEW_START_DATES:
        start_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(
            hour=12, tzinfo=datetime.UTC
        )

        existing_qs = HistoricalAssignment.objects.filter(
            id=assignment_pk,
            history_type="+",
            rfc_to_be__draft__name=draft_name,
        )
        count = existing_qs.count()
        if count != 1:
            logger.warning(
                "backfill_final_review_history: expected 1 history entry for %s "
                "assignment #%d, found %d, skipping",
                draft_name,
                assignment_pk,
                count,
            )
            skipped += 1
            continue
        existing = existing_qs.get()

        if existing.history_date == start_date:
            logger.info(
                "backfill_final_review_history: %s assignment #%d already has "
                "correct date %s, skipping",
                draft_name,
                assignment_pk,
                date_str,
            )
            skipped += 1
            continue
        if not dry_run:
            existing.history_date = start_date
            existing.history_change_reason = (
                "Added (Backfilled final review start date)"
            )
            existing.save(update_fields=["history_date", "history_change_reason"])
        prefix = "[DRY RUN] " if dry_run else ""
        logger.info(
            "backfill_final_review_history: %supdated history_date for %s "
            "assignment #%d → %s",
            prefix,
            draft_name,
            assignment_pk,
            date_str,
        )
        added += 1

    return added, skipped
