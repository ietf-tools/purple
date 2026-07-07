# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


def backfill_rev(apps, schema_editor):
    RfcToBe = apps.get_model("rpc", "RfcToBe")
    for rfctobe in RfcToBe.objects.filter(rev="", draft__isnull=False).select_related("draft"):
        if rfctobe.draft.rev:
            rfctobe.rev = rfctobe.draft.rev
            rfctobe.save(update_fields=["rev"])


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0009_populate_rfctobe_published_formats"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="rev",
            field=models.CharField(
                blank=True,
                help_text="Revision of draft being worked on. Overrides draft.rev "
                "when set.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="rev",
            field=models.CharField(
                blank=True,
                help_text="Revision of draft being worked on. Overrides draft.rev "
                "when set.",
                max_length=16,
            ),
        ),
        migrations.RunPython(backfill_rev, migrations.RunPython.noop),
    ]
