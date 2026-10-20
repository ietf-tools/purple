# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0019_mailmessage_intake_msgtype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("unblocked", "document unblocked"),
                    ("repo_not_created", "document repo not created"),
                ],
                max_length=32,
            ),
        ),
    ]
