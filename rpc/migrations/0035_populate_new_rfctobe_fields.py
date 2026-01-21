# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations
from django.db.models import F


def forward(apps, schema_editor):
    RfcToBe = apps.get_model("rpc", "RfcToBe")
    # These are all unknown
    RfcToBe.objects.update(
        boilerplate=F("intended_boilerplate"),
    )

    # intended_std_level holds our best info as to current status
    RfcToBe.objects.update(
        std_level=F("intended_std_level"),
        stream=F("intended_stream"),
    )
    RfcToBe.objects.filter(disposition="published").update(
        publication_std_level=F("submitted_std_level"),
    )
    RfcToBe.objects.filter(disposition="published").exclude(
        intended_stream="legacy"
    ).update(
        publication_stream=F("intended_stream"),
    )


def reverse(apps, schema_editor):
    pass  # nothing to do


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0034_more_rfctobe_fields"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
