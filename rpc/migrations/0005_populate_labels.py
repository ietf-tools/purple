# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations

COMPLEXITY_COLOR = "green"


def forward(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    for slug in [
        "bis",
        "cluster: easy",
        "cluster: medium",
        "cluster: hard",
        "abnf code",
        "mib code",
        "xml code",
        "yang code",
        "iana: easy",
        "iana: medium",
        "iana: hard",
        "status change",
        "xml formatting: easy",
        "xml formatting: medium",
        "xml formatting: hard",
    ]:
        Label.objects.create(
            slug=slug, is_exception=False, is_complexity=True, color=COMPLEXITY_COLOR
        )
    Label.objects.create(
        slug="expedited", is_exception=True, is_complexity=True, color=COMPLEXITY_COLOR
    )


def reverse(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    Label.objects.filter(is_complexity=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0004_populate_capability"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
