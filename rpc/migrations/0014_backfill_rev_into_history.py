# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


def backfill_rev_into_history(apps, schema_editor):
    """Write RfcToBe.rev onto its existing historical snapshots.

    0010 set rev without creating history (migrations bypass simple-history), so
    the value would otherwise surface as a spurious change on the next editor's
    save.
    """
    RfcToBe = apps.get_model("rpc", "RfcToBe")
    Historical = apps.get_model("rpc", "HistoricalRfcToBe")
    for rfctobe in RfcToBe.objects.exclude(rev=""):
        Historical.objects.filter(id=rfctobe.id).update(rev=rfctobe.rev)


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0013_historicallabel_is_public_label_is_public"),
    ]

    operations = [
        migrations.RunPython(backfill_rev_into_history, migrations.RunPython.noop),
    ]
