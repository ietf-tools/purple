# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0006_populate_doc_relationship_names"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="rpcrelateddocument",
            constraint=models.UniqueConstraint(
                condition=models.Q(("target_document__isnull", False)),
                fields=("source", "target_document"),
                name="unique_source_targetdoc",
                violation_error_message="A source/target_document relationship must "
                "be unique.",
            ),
        ),
        migrations.AddConstraint(
            model_name="rpcrelateddocument",
            constraint=models.UniqueConstraint(
                condition=models.Q(("target_rfctobe__isnull", False)),
                fields=("source", "target_rfctobe"),
                name="unique_source_targetrfctobe",
                violation_error_message="A source/target_rfctobe relationship must "
                "be unique.",
            ),
        ),
    ]
