# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0013_alter_actionholder_body"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="rfcauthor",
            constraint=models.UniqueConstraint(
                fields=("datatracker_person", "rfc_to_be"),
                name="unique_author_per_document",
                violation_error_message="the person is already an author of this"
                " document",
            ),
        ),
    ]
