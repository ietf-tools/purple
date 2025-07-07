# Copyright The IETF Trust 2025, All Rights Reserved

import django.db.models.constraints
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0004_historicaldatatrackerperson"),
        ("rpc", "0018_alter_historicalrfctobe_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="rfcauthor",
            options={"ordering": ["rfc_to_be", "order"]},
        ),
        migrations.AddField(
            model_name="rfcauthor",
            name="order",
            field=models.PositiveIntegerField(
                null=True, help_text="Order of the author on the document"
            ),
        ),
        migrations.AddConstraint(
            model_name="rfcauthor",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("rfc_to_be", "order"),
                name="unique_author_order_per_document",
                violation_error_message="each author order must be unique per document",
            ),
        ),
    ]
