# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0011_delete_ianaaction"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="historicalrfctobe",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical rfc to be",
                "verbose_name_plural": "historical rfc to bes",
            },
        ),
        migrations.AlterModelOptions(
            name="rfctobe",
            options={},
        ),
        migrations.AlterField(
            model_name="historicalrfctobe",
            name="rfc_number",
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="rfctobe",
            name="rfc_number",
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
        migrations.AddConstraint(
            model_name="rfctobe",
            constraint=models.UniqueConstraint(
                fields=("rfc_number",),
                name="unique_non_null_rfc_number",
                nulls_distinct=True,
            ),
        ),
    ]
