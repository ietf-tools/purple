# Copyright The IETF Trust 2026, All Rights Reserved

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("datatracker", "0002_initial"),
        ("rpc", "0032_alter_mailmessage_cc_alter_mailmessage_message_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalrfctobe",
            name="title",
            field=models.CharField(
                default="<title missing>", help_text="Document title", max_length=255
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="boilerplate",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="TLP IPR boilerplate option",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.tlpboilerplatechoicename",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="group",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Acronym of datatracker group where this document originated, "
                    "if any"
                ),
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="iesg_contact",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Responsible or shepherding AD, if any",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="datatracker.datatrackerperson",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="keywords",
            field=models.CharField(
                blank=True,
                help_text="Comma-separated list of keywords",
                max_length=1000,
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="pages",
            field=models.PositiveIntegerField(help_text="Page count", null=True),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="publication_std_level",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="StdLevel at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="publication_stream",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Stream at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="shepherd",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Document shepherd",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="datatracker.datatrackerperson",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="std_level",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Current StdLevel",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="historicalrfctobe",
            name="stream",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="Current stream",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="title",
            field=models.CharField(
                default="<title missing>", help_text="Document title", max_length=255
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="boilerplate",
            field=models.ForeignKey(
                default="unknown",
                help_text="TLP IPR boilerplate option",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.tlpboilerplatechoicename",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="group",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Acronym of datatracker group where this document originated, "
                    "if any"
                ),
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="iesg_contact",
            field=models.ForeignKey(
                blank=True,
                help_text="Responsible or shepherding AD, if any",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="datatracker.datatrackerperson",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="keywords",
            field=models.CharField(
                blank=True,
                help_text="Comma-separated list of keywords",
                max_length=1000,
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="pages",
            field=models.PositiveIntegerField(help_text="Page count", null=True),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="publication_std_level",
            field=models.ForeignKey(
                blank=True,
                help_text="StdLevel at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="publication_stream",
            field=models.ForeignKey(
                blank=True,
                help_text="Stream at publication (blank until published)",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="shepherd",
            field=models.ForeignKey(
                blank=True,
                help_text="Document shepherd",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="shepherded_rfctobe_set",
                to="datatracker.datatrackerperson",
            ),
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="std_level",
            field=models.ForeignKey(
                default="unkn",
                help_text="Current StdLevel",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.stdlevelname",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rfctobe",
            name="stream",
            field=models.ForeignKey(
                default="ietf",
                help_text="Current stream",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="rpc.streamname",
            ),
            preserve_default=False,
        ),
    ]
