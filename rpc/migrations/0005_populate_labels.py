# Copyright The IETF Trust 2025-2026, All Rights Reserved

from django.db import migrations
from simple_history.utils import bulk_create_with_history

COMPLEXITY_COLOR = "green"


def forward(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")

    labels = []
    for slug in [
        "bis",
        "cluster: easy",
        "cluster: medium",
        "cluster: hard",
        "code: abnf",
        "code: mib",
        "code: xml",
        "code: yang",
        "iana: easy",
        "iana: medium",
        "iana: hard",
        "status change",
        "xml formatting: easy",
        "xml formatting: medium",
        "xml formatting: hard",
        "refs: easy",
        "refs: hard",
        "Fast Track",
    ]:
        labels.append(
            Label(
                slug=slug,
                is_exception=False,
                is_complexity=True,
                color=COMPLEXITY_COLOR,
            )
        )

    labels.append(
        Label(
            slug="Expedited",
            is_exception=True,
            is_complexity=True,
            color=COMPLEXITY_COLOR,
        )
    )

    bulk_create_with_history(
        labels, Label, batch_size=100, default_change_reason="Created during migration"
    )


def reverse(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    Label.objects.filter(is_complexity=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0004_populate_capability"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
