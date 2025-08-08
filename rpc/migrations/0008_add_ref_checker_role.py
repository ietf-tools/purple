# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations


class Migration(migrations.Migration):
    def forward(apps, schema_editor):
        RpcRole = apps.get_model("rpc", "RpcRole")
        RpcRole.objects.create(
            slug="ref_checker",
            name="Reference Checker",
            desc="Normative Reference Checker",
        )

    def reverse(apps, schema_editor):
        RpcRole = apps.get_model("rpc", "RpcRole")
        RpcRole.objects.filter(slug="ref_checker").delete()

    dependencies = [
        ("rpc", "0007_rpcrelateddocument_unique_source_targetdoc_and_more"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
