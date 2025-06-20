# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    DocRelationshipName = apps.get_model("rpc", "DocRelationshipName")

    DocRelationshipName.objects.create(
        slug="missref",
        name="Missreference",
        desc="Normative reference to a document that is still in draft state",
        used=True,
    )


def reverse(apps, schema_editor):
    DocRelationshipName = apps.get_model("rpc", "DocRelationshipName")
    DocRelationshipName.objects.filter(
        slug__in=[
            "misref",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0014_rfcauthor_unique_author_per_document"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
