# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0007_populate_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicallabel",
            name="slug",
            field=models.CharField(db_index=True, max_length=64),
        ),
        migrations.AlterField(
            model_name="label",
            name="slug",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
