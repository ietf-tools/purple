# Copyright The IETF Trust 2025, All Rights Reserved

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0008_alter_historicallabel_slug_alter_label_slug"),
    ]

    operations = [
        migrations.DeleteModel(
            name="IanaAction",
        ),
        migrations.AddField(
            model_name="actionholder",
            name="body",
            field=models.CharField(
                blank=True,
                choices=[("", "None"), ("iana", "IANA")],
                default="",
                max_length=64,
            ),
        ),
        migrations.AddConstraint(
            model_name="actionholder",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("completed__isnull", True),
                    ("datatracker_person__isnull", False),
                    _connector="OR",
                ),
                name="actionholder_completion_requires_person",
                violation_error_message="completion requires a person",
            ),
        ),
    ]
