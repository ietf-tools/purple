# Copyright The IETF Trust 2026, All Rights Reserved

import datetime
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)

# (draft_name, start_date) — start_date is when the final_review_editor assignment was
# created
FINAL_REVIEW_START_DATES = [
    ("draft-ietf-tls-rfc8446bis", "2025-12-15"),
    ("draft-ietf-tls-keylogfile", "2025-12-16"),
    ("draft-ietf-tls-tls12-frozen", "2026-01-05"),
    ("draft-ietf-uta-require-tls13", "2026-01-06"),
    ("draft-ietf-stir-servprovider-oob", "2025-10-21"),
    ("draft-ietf-pce-pceps-tls13", "2026-01-16"),
    ("draft-ietf-netconf-over-tls13", "2026-01-16"),
    ("draft-ietf-lamps-rfc5019bis", "2026-01-16"),
    ("draft-ietf-pce-sid-algo", "2026-02-19"),
    ("draft-ietf-cose-merkle-tree-proofs", "2026-03-06"),
    ("draft-ietf-scitt-architecture", "2026-03-06"),
    ("draft-ietf-tls-hybrid-design", "2026-04-03"),
    ("draft-ietf-pquip-hybrid-signature-spectrums", "2026-04-03"),
    ("draft-ietf-pquip-pqc-engineers", "2026-04-27"),
    ("draft-ietf-emu-bootstrapped-tls", "2026-04-27"),
    ("draft-ietf-stir-rfc4916-update", "2026-05-01"),
    ("draft-ietf-bmwg-mlrsearch", "2026-05-13"),
    ("draft-ietf-tls-8773bis", "2026-04-06"),
    ("draft-ietf-bier-oam-requirements", "2026-05-04"),
    ("draft-ietf-dnsop-cds-consistency", "2026-05-06"),
    ("draft-ietf-opsawg-prefix-lengths", "2026-05-06"),
    ("draft-ietf-bfd-stability", "2026-05-07"),
    ("draft-ietf-mailmaint-messageflag-mailboxattribute", "2026-05-07"),
    ("draft-ietf-openpgp-pqc", "2026-05-08"),
    ("draft-ietf-sidrops-manifest-numbers", "2026-05-08"),
    ("draft-ietf-calext-jscontact-uid", "2026-05-12"),
    ("draft-ietf-netconf-udp-client-server", "2026-05-13"),
    ("draft-ietf-bfd-optimizing-authentication", "2026-05-19"),
    ("draft-ietf-sshm-ssh-agent", "2026-05-14"),
    ("draft-ietf-avtcore-rtp-haptics", "2026-05-18"),
]


def backfill_final_review_history(dry_run: bool = False) -> tuple[int, int]:
    """Backfill missing history creation entries for final_review_editor assignments.

    Returns (added, skipped).
    """
    from rpc.models import Assignment, RfcToBe

    HistoricalAssignment = Assignment.history.model
    added = 0
    skipped = 0

    for draft_name, date_str in FINAL_REVIEW_START_DATES:
        start_date = timezone.make_aware(
            datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=12)
        )

        rfctobe = (
            RfcToBe.objects.filter(draft__name=draft_name)
            .select_related("draft")
            .first()
        )
        if not rfctobe:
            logger.warning(
                "backfill_final_review_history: no RfcToBe found for %s", draft_name
            )
            skipped += 1
            continue

        assignments = Assignment.objects.filter(
            rfc_to_be=rfctobe,
            role__slug="final_review_editor",
        ).select_related("role", "person")

        if not assignments.exists():
            logger.warning(
                "backfill_final_review_history: no final_review_editor assignment "
                "for %s",
                rfctobe.name,
            )
            skipped += 1
            continue

        for assignment in assignments:
            existing = HistoricalAssignment.objects.filter(
                id=assignment.id, history_type="+"
            ).first()

            if existing:
                if existing.history_date == start_date:
                    logger.info(
                        "backfill_final_review_history: %s assignment #%s already has "
                        "correct date %s, skipping",
                        rfctobe.name, assignment.id, date_str,
                    )
                    skipped += 1
                    continue
                if not dry_run:
                    existing.history_date = start_date
                    existing.save(update_fields=["history_date"])
                prefix = "[DRY RUN] " if dry_run else ""
                logger.info(
                    "backfill_final_review_history: %supdated history_date for %s "
                    "assignment #%s → %s",
                    prefix, rfctobe.name, assignment.id, date_str,
                )
            else:
                if not dry_run:
                    HistoricalAssignment.objects.create(
                        id=assignment.id,
                        rfc_to_be=rfctobe,
                        person=assignment.person,
                        role=assignment.role,
                        state=assignment.state,
                        comment=assignment.comment,
                        time_spent=assignment.time_spent,
                        history_date=start_date,
                        history_type="+",
                        history_user=None,
                        history_change_reason="Backfilled final review start date",
                    )
                prefix = "[DRY RUN] " if dry_run else ""
                logger.info(
                    "backfill_final_review_history: %screated history for %s "
                    "assignment #%s → %s",
                    prefix, rfctobe.name, assignment.id, date_str,
                )
            added += 1

    return added, skipped
