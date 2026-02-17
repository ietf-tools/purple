# Copyright The IETF Trust 2025-2026, All Rights Reserved

from django.db import migrations
from django.utils import timezone

COMPLEXITY_COLOR = "green"


def forward(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    HistoricalLabel = apps.get_model("rpc", "HistoricalLabel")

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

    # Bulk create labels
    created_labels = Label.objects.bulk_create(labels)

    # Manually create history records
    history_records = []
    history_date = timezone.now()
    for label in created_labels:
        history_records.append(
            HistoricalLabel(
                id=label.id,
                slug=label.slug,
                is_exception=label.is_exception,
                is_complexity=label.is_complexity,
                color=label.color,
                history_date=history_date,
                history_change_reason="Created during migration",
                history_type="+",
            )
        )

    HistoricalLabel.objects.bulk_create(history_records)


def reverse(apps, schema_editor):
    Label = apps.get_model("rpc", "Label")
    Label.objects.filter(is_complexity=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0004_populate_capability"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
