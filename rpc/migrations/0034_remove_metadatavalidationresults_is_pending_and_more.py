# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0033_metadatavalidationresults"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="metadatavalidationresults",
            name="is_pending",
        ),
        migrations.AddField(
            model_name="metadatavalidationresults",
            name="detail",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="metadatavalidationresults",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("success", "Success"),
                    ("failed", "Failed"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
