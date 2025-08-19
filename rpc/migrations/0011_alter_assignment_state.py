# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0010_historicallabel_used_label_used"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignment",
            name="state",
            field=models.CharField(
                choices=[
                    ("assigned", "Assigned"),
                    ("in_progress", "In Progress"),
                    ("done", "Done"),
                    ("withdrawn", "Withdrawn"),
                ],
                default="assigned",
                max_length=32,
            ),
        ),
    ]
