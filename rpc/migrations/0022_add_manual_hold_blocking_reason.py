# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    BlockingReason = apps.get_model("rpc", "BlockingReason")
    BlockingReason.objects.get_or_create(
        slug="manual_hold", defaults={"name": "Manual Hold"}
    )


def reverse(apps, schema_editor):
    BlockingReason = apps.get_model("rpc", "BlockingReason")
    BlockingReason.objects.filter(slug="manual_hold").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0021_dirtybits"),
    ]
    operations = [migrations.RunPython(forward, reverse)]
