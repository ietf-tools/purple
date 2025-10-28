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
                fields=("source", "target_document", "target_rfctobe", "relationship"),
                name="unique_source_target_relationship",
                violation_error_message="A source/target relationship must be unique "
                "per relationship type.",
            ),
        ),
    ]
