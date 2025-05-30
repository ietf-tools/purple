# Copyright The IETF Trust 2023, All Rights Reserved

from django.db import migrations


def forward(apps, schema_editor):
    RpcRole = apps.get_model("rpc", "RpcRole")
    RpcRole.objects.create(slug="enqueuer", name="Enqueuer", desc="Submission enqueuer")
    RpcRole.objects.create(
        slug="formatting", name="Formatting", desc="RFCXML formatter"
    )
    RpcRole.objects.create(
        slug="first_editor", name="First editor", desc="First editor of an RFC"
    )  # was "pe"
    RpcRole.objects.create(
        slug="second_editor", name="Second editor", desc="Second editor of an RFC"
    )  # was "re"
    RpcRole.objects.create(
        slug="final_review_editor",
        name="Final review editor",
        desc="Performs editing during Final Review",
    )
    RpcRole.objects.create(slug="publisher", name="Publisher", desc="RFC publisher")
    RpcRole.objects.create(slug="manager", name="Manager", desc="RPC Manager")


def reverse(apps, schema_editor):
    RpcRole = apps.get_model("rpc", "RpcRole")
    RpcRole.objects.filter(
        slug__in=[
            "formatting",
            "first_editor",
            "second_editor",
            "final_review_editor",
            "publisher",
            "manager",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0002_populate_names"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
