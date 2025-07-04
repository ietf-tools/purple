# Copyright The IETF Trust 2025, All Rights Reserved

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
                default=0, help_text="Order of the author on the document"
            ),
        ),
        migrations.AddConstraint(
            model_name="rfcauthor",
            constraint=models.UniqueConstraint(
                condition=models.Q(("order", 0), _negated=True),
                fields=("rfc_to_be", "order"),
                name="unique_nonzero_author_order_per_document",
                violation_error_message="each nonzero author order must be unique per "
                "document",
            ),
        ),
    ]
