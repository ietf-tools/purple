# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0032_alter_mailmessage_cc_alter_mailmessage_message_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MetadataValidationResults",
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
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("is_valid", models.BooleanField()),
                (
                    "head_sha",
                    models.CharField(
                        help_text="Head SHA of the commit that was validated",
                        max_length=40,
                    ),
                ),
                ("metadata", models.JSONField()),
                (
                    "rfc_to_be",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="rpc.rfctobe"
                    ),
                ),
            ],
            options={
                "ordering": ["-received_at"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("rfc_to_be",),
                        name="unique_metadata_validation_per_rfc_to_be",
                        violation_error_message=(
                            "There can be only one MetadataValidationResults per "
                            "rfc_to_be.",
                        ),
                    ),
                    models.UniqueConstraint(
                        fields=("head_sha",),
                        name="unique_metadata_validation_per_head_sha",
                        violation_error_message=(
                            "There can be only one MetadataValidationResults per "
                            "head_sha.",
                        ),
                    ),
                ],
            },
        ),
    ]
