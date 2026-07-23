# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


def set_existing_labels_public(apps, schema_editor):
    # Existing labels were all public before this flag existed; the field
    # default (False) applies only to labels created afterwards.
    Label = apps.get_model("rpc", "Label")
    Label.objects.update(is_public=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0011_historicalactionholder_historicalrpcauthorcomment_and_more"),
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
        migrations.RunPython(set_existing_labels_public, noop),
    ]
