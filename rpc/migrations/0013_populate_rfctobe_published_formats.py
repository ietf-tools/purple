# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    PublishedFormatName = apps.get_model("rpc", "PublishedFormatName")
    PublishedFormatName.objects.create(slug="txt", name="Text")
    PublishedFormatName.objects.create(slug="html", name="HTML")
    PublishedFormatName.objects.create(slug="pdf", name="PDF")
    PublishedFormatName.objects.create(slug="xml", name="XML")
    PublishedFormatName.objects.create(slug="ps", name="PostScript")
    PublishedFormatName.objects.create(slug="notprepped", name="Not prepped XML")


def reverse(apps, schema_editor):
    PublishedFormatName = apps.get_model("rpc", "PublishedFormatName")
    PublishedFormatName.objects.filter(
        slug__in=[
            "txt",
            "html",
            "pdf",
            "xml",
            "ps",
            "notprepped",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0012_publishedformatname_rfctobe_published_formats"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
