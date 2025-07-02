# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0014_rfcauthor_unique_author_per_document"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rpcperson",
            name="can_hold_role",
            field=models.ManyToManyField(blank=True, to="rpc.rpcrole"),
        ),
        migrations.AlterField(
            model_name="rpcperson",
            name="capable_of",
            field=models.ManyToManyField(blank=True, to="rpc.capability"),
        ),
        migrations.AlterField(
            model_name="rpcperson",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"can_hold_role__slug": "manager"},
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="managed_people",
                to="rpc.rpcperson",
            ),
        ),
    ]
