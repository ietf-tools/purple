# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations
from django.utils import timezone


def record_rev_backfill_history(apps, schema_editor):
    """Record the rev backfill from 0010 as a System history entry.

    0010 set RfcToBe.rev without creating history (migrations bypass
    simple-history), so the change would otherwise surface on — and be
    misattributed to — the next editor's save. For any draft whose latest
    snapshot hasn't captured the current rev, add one entry with
    history_user=None ("(System)") so it's attributed correctly and no longer
    appears on the next edit.
    """
    RfcToBe = apps.get_model("rpc", "RfcToBe")
    Historical = apps.get_model("rpc", "HistoricalRfcToBe")
    field_names = [f.attname for f in RfcToBe._meta.fields]
    now = timezone.now()

    for rfctobe in RfcToBe.objects.exclude(rev=""):
        latest = (
            Historical.objects.filter(id=rfctobe.id)
            .order_by("-history_date", "-history_id")
            .first()
        )
        # Already reflected in history (e.g. edited since 0010) — skip.
        if latest is None or latest.rev == rfctobe.rev:
            continue
        Historical.objects.create(
            **{name: getattr(rfctobe, name) for name in field_names},
            history_date=now,
            history_type="~",
            history_change_reason="rev backfilled from draft revision",
            history_user_id=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0011_historicalactionholder_historicalrpcauthorcomment_and_more"),
    ]

    operations = [
        migrations.RunPython(record_rev_backfill_history, migrations.RunPython.noop),
    ]
