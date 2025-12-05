# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models

import rpc.models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0025_alter_historicalrfctobe_iana_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rfctobe",
            name="rfc_number",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                unique=True,
                validators=[rpc.models.validate_not_unusable_rfc_number],
            ),
        ),
    ]
