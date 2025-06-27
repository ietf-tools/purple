# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations


def add_status_data(apps, schema_editor):
    Status = apps.get_model("errata", "Status")
    statuses = [
        {
            "slug": "verified",
            "name": "Verified",
            "desc": "Erratum has been verified by Stream Specific Party",
        },
        {
            "slug": "reported",
            "name": "Reported",
            "desc": "Erratum is reported, but not verified",
        },
        {
            "slug": "held_for_doc_update",
            "name": "Held for Document Update",
            "desc": "Erratum not verified, but should be reexamined when the RFC is "
            "updated or deprecated.",
        },
        {"slug": "sort_fix", "name": "Sort-Fix", "desc": "Fixing sort order."},
        {"slug": "rejected", "name": "Rejected", "desc": "This erratum was rejected."},
    ]
    for status in statuses:
        Status.objects.create(**status)


def remove_status_data(apps, schema_editor):
    Status = apps.get_model("errata", "Status")
    slugs = ["verified", "reported", "held_for_document_update", "sort_fix", "rejected"]
    Status.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("errata", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_status_data, remove_status_data),
    ]
