# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0016_alter_assignment_state_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="assignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("state__in", ["done", "withdrawn", "closed_for_hold"]),
                    _negated=True,
                ),
                fields=("person", "rfc_to_be", "role"),
                name="unique_active_assignment_per_person_rfc_role",
                violation_error_message="A person can only have one active assignment "
                "per RFC and role",
            ),
        ),
    ]
