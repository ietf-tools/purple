# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


def backfill_rev_into_history(apps, schema_editor):
    """Fill the rev that 0010 set into the snapshots that never recorded it.

    0010 set RfcToBe.rev without creating history (migrations bypass
    simple-history), so the value would otherwise surface as a change on
    the next editor's save. Only the empty ('') snapshots — the ones predating
    the field being populated — are filled, with the earliest rev history did
    record; genuine rev values are left untouched.
    """
    RfcToBe = apps.get_model("rpc", "RfcToBe")
    Historical = apps.get_model("rpc", "HistoricalRfcToBe")
    for rfctobe in RfcToBe.objects.exclude(rev=""):
        snaps = Historical.objects.filter(id=rfctobe.id)
        first_real = (
            snaps.exclude(rev="")
            .order_by("history_date", "history_id")
            .values_list("rev", flat=True)
            .first()
        ) or rfctobe.rev
        snaps.filter(rev="").update(rev=first_real)


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0013_historicallabel_is_public_label_is_public"),
    ]

    operations = [
        migrations.RunPython(backfill_rev_into_history, migrations.RunPython.noop),
    ]
