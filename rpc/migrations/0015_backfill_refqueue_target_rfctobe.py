# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations
from django.utils import timezone

CHANGE_REASON = "backfill: link refqueue target to RfcToBe (migration 0015)"


def _write_history(Historical, ref, history_type):
    """Record a simple-history snapshot for a row this migration mutated.

    Migrations bypass simple-history's signals, so without this the next in-app
    save would diff against the pre-migration snapshot and misattribute this
    change to that editor. Attributed to no user, tagged with a change reason.
    """
    Historical.objects.create(
        id=ref.pk,
        relationship_id=ref.relationship_id,
        source_id=ref.source_id,
        target_document_id=ref.target_document_id,
        target_rfctobe_id=ref.target_rfctobe_id,
        history_date=timezone.now(),
        history_type=history_type,
        history_change_reason=CHANGE_REASON,
        history_user_id=None,
    )


def backfill_refqueue_targets(apps, schema_editor):
    """Re-link refqueue references from target_document to target_rfctobe.

    A refqueue row created before its target entered the queue points at the
    datatracker Document. Once the target has an RfcToBe, the blocking gates and
    the signal-driven re-evaluation both key off target_rfctobe, so such rows are
    invisible to them. Convert each to point at the active RfcToBe (exactly one
    target may be set, so target_document is cleared). Drop rows that would
    duplicate an existing target_rfctobe reference.
    """
    RpcRelatedDocument = apps.get_model("rpc", "RpcRelatedDocument")
    HistoricalRpcRelatedDocument = apps.get_model("rpc", "HistoricalRpcRelatedDocument")
    RfcToBe = apps.get_model("rpc", "RfcToBe")

    stale = RpcRelatedDocument.objects.filter(
        relationship_id="refqueue",
        target_rfctobe__isnull=True,
        target_document__isnull=False,
    )
    for ref in stale:
        rfctobe = (
            RfcToBe.objects.filter(draft=ref.target_document)
            .exclude(disposition_id="withdrawn")
            .first()
        )
        if rfctobe is None:
            continue  # genuinely external / not in the queue
        duplicate = (
            RpcRelatedDocument.objects.filter(
                source=ref.source,
                target_rfctobe=rfctobe,
                relationship_id="refqueue",
            )
            .exclude(pk=ref.pk)
            .exists()
        )
        if duplicate:
            _write_history(
                HistoricalRpcRelatedDocument, ref, "-"
            )  # snapshot pre-delete state
            ref.delete()
            continue
        ref.target_document = None
        ref.target_rfctobe = rfctobe
        ref.save(update_fields=["target_document", "target_rfctobe"])
        _write_history(HistoricalRpcRelatedDocument, ref, "~")


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0014_backfill_rev_into_history"),
    ]

    operations = [
        migrations.RunPython(backfill_refqueue_targets, migrations.RunPython.noop),
    ]
