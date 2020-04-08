# Generated by Django 3.0.5 on 2020-04-07 22:51

from django.db import migrations, models

import localhub.activities.validators


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0020_auto_20200318_2200"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalpost",
            name="additional_tags",
            field=models.CharField(
                blank=True,
                max_length=300,
                validators=[localhub.activities.validators.validate_hashtags],
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="additional_tags",
            field=models.CharField(
                blank=True,
                max_length=300,
                validators=[localhub.activities.validators.validate_hashtags],
            ),
        ),
    ]