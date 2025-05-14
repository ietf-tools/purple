# Copyright The IETF Trust 2024, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("datatracker", "0001_initial"),
        ("rpc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="documentlabel",
            name="label",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="rpc.label"
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="labels",
            field=models.ManyToManyField(
                through="datatracker.DocumentLabel", to="rpc.label"
            ),
        ),
    ]
