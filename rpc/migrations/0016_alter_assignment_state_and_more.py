# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0015_rfcauthor_affiliation"),
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
                    ("closed_for_hold", "Closed For Hold"),
                ],
                default="assigned",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="historicalassignment",
            name="state",
            field=models.CharField(
                choices=[
                    ("assigned", "Assigned"),
                    ("in_progress", "In Progress"),
                    ("done", "Done"),
                    ("withdrawn", "Withdrawn"),
                    ("closed_for_hold", "Closed For Hold"),
                ],
                default="assigned",
                max_length=32,
            ),
        ),
    ]
