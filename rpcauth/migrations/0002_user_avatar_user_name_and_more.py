# Copyright The IETF Trust 2023, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpcauth", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="name",
            field=models.CharField(
                default="Unknown", help_text="User's name", max_length=255
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="datatracker_subject_id",
            field=models.CharField(
                help_text="Datatracker's subject ID for this User",
                max_length=255,
                null=True,
                unique=True,
            ),
        ),
    ]
