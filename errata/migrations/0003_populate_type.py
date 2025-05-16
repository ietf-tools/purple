# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations


def add_type_data(apps, schema_editor):
    Type = apps.get_model("errata", "Type")
    types = [
        {"slug": "editorial", "name": "Editorial"},
        {"slug": "technical", "name": "Technical"},
    ]
    for type in types:
        Type.objects.create(**type)


def remove_type_data(apps, schema_editor):
    Type = apps.get_model("errata", "Type")
    slugs = ["editorial", "technical"]
    Type.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("errata", "0002_populate_status"),
    ]

    operations = [
        migrations.RunPython(add_type_data, remove_type_data),
    ]
