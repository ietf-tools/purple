# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0018_editorialnote"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mailmessage",
            name="msgtype",
            field=models.CharField(
                choices=[
                    ("blank", "freeform"),
                    ("finalreview", "final review notification"),
                    ("publication", "publication announcement"),
                    ("enqueuing", "enqueuing notification"),
                    ("intake", "intake form"),
                ],
                max_length=64,
            ),
        ),
    ]
