# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0003_historicaldocument_historicaldocumentlabel"),
        ("rpc", "0019_mailmessage_intake_msgtype"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="actionholder",
            name="actionholder_completion_requires_person",
        ),
        migrations.AlterField(
            model_name="clustermember",
            name="doc",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="datatracker.document"
            ),
        ),
        migrations.AlterField(
            model_name="editorialnote",
            name="rfc_to_be",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="editorial_note",
                to="rpc.rfctobe",
            ),
        ),
        migrations.AlterField(
            model_name="rpcperson",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"can_hold_role__slug": "manager"},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="managed_people",
                to="rpc.rpcperson",
            ),
        ),
    ]
