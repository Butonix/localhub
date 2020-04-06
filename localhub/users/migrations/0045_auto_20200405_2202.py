# Generated by Django 3.0.4 on 2020-04-05 22:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0044_historicaluser"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaluser",
            name="dismissed_notices",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=30), default=list, size=None
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="dismissed_notices",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=30), default=list, size=None
            ),
        ),
    ]
