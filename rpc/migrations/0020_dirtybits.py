# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0019_add_stream_manager_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="DirtyBits",
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
                (
                    "slug",
                    models.CharField(
                        choices=[("rfcindex", "RFC Index")], max_length=40, unique=True
                    ),
                ),
                ("dirty_time", models.DateTimeField(blank=True, null=True)),
                ("processed_time", models.DateTimeField(blank=True, null=True)),
            ],
            options={"verbose_name_plural": "dirty bits"},
        ),
    ]
