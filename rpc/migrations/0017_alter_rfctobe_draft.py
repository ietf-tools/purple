# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0016_populate_doc_relationship_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rfctobe",
            name="draft",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="datatracker.document",
            ),
        ),
    ]
