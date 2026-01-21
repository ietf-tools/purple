# Copyright The IETF Trust 2026, All Rights Reserved

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rpc", "0034_populate_new_rfctobe_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="intended_boilerplate",
        ),
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="intended_std_level",
        ),
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="intended_stream",
        ),
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="submitted_boilerplate",
        ),
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="submitted_std_level",
        ),
        migrations.RemoveField(
            model_name="historicalrfctobe",
            name="submitted_stream",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="intended_boilerplate",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="intended_std_level",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="intended_stream",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="submitted_boilerplate",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="submitted_std_level",
        ),
        migrations.RemoveField(
            model_name="rfctobe",
            name="submitted_stream",
        ),
    ]
