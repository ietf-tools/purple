# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0003_document_group"),
        ("rpc", "0015_taskrun"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="rfctobe",
            constraint=models.UniqueConstraint(
                condition=models.Q(("disposition_id", "withdrawn"), _negated=True),
                fields=("draft",),
                name="unique_active_rfctobe_per_draft",
                violation_error_message="A draft can only have one non-withdrawn "
                "RfcToBe",
            ),
        ),
    ]
