# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0017_assignment_unique_active_assignment_per_person_rfc_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubseriesMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.PositiveIntegerField()),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
                (
                    "std_level",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rpc.stdlevelname",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("rfc_to_be",),
                        name="unique_rfctobe",
                        violation_error_message="Each RFC can only belong to a "
                        "subseries once",
                    )
                ],
            },
        ),
    ]
