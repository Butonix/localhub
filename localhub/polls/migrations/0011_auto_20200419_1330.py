# Generated by Django 3.0.5 on 2020-04-19 13:30

from django.db import migrations, models

import localhub.users.validators


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0010_auto_20200408_1326"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpoll",
            name="mentions",
            field=models.CharField(
                blank=True,
                max_length=300,
                validators=[localhub.users.validators.validate_mentions],
            ),
        ),
        migrations.AddField(
            model_name="poll",
            name="mentions",
            field=models.CharField(
                blank=True,
                max_length=300,
                validators=[localhub.users.validators.validate_mentions],
            ),
        ),
    ]
