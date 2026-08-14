# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models
from django.utils import timezone


def set_used_labels_public(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    Historical = apps.get_model("rpc", "HistoricalLabel")
    field_names = [f.attname for f in Label._meta.fields]
    now = timezone.now()
    for label in Label.objects.filter(used=True):
        label.is_public = True
        label.save(update_fields=["is_public"])
        Historical.objects.create(
            **{name: getattr(label, name) for name in field_names},
            history_date=now,
            history_type="~",
            history_change_reason="backfill is_public for existing labels",
            history_user_id=None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0012_remove_historicalrfctobe_publication_stream_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicallabel",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="label",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_used_labels_public, migrations.RunPython.noop),
    ]
