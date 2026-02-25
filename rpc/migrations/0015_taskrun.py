# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0014_historicaladditionalemail_historicalrfcauthor_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskRun",
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
                ("task_name", models.CharField(max_length=255, unique=True)),
                ("last_run_at", models.DateTimeField()),
                ("is_running", models.BooleanField(default=False)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("is_running", True)),
                        fields=("task_name",),
                        name="unique_running_task",
                        violation_error_message="This task is already running",
                    )
                ],
            },
        ),
    ]
