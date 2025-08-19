# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


def forward(apps, schema_editor):
    Assignment = apps.get_model("rpc", "Assignment")
    Assignment.objects.filter(state="in progress").update(state="in_progress")


def reverse(apps, schema_editor):
    Assignment = apps.get_model("rpc", "Assignment")
    Assignment.objects.filter(state="in_progress").update(state="in progress")


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0010_historicallabel_used_label_used"),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
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
