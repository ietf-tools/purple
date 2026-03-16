# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0017_publicationattempt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="publicationattempt",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("failed", "Failed")],
                default="pending",
                help_text="Record of an RFC publication request",
                max_length=20,
            ),
        ),
    ]
