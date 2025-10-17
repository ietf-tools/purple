# Copyright The IETF Trust 2023-2025, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    SubseriesType = apps.get_model("rpc", "SubseriesType")
    SubseriesType.objects.create(slug="bcp", name="Best Current Practice")
    SubseriesType.objects.create(slug="std", name="Internet Standard")
    SubseriesType.objects.create(slug="fyi", name="For Your Information")


def reverse(apps, schema_editor):
    SubseriesType = apps.get_model("rpc", "SubseriesType")
    SubseriesType.objects.filter(
        slug__in=[
            "bcp",
            "std",
            "fyi",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0018_subseriestype_historicalsubseriesmember_and_more"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
