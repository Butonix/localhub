# Generated by Django 2.2.4 on 2019-09-08 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0014_auto_20190906_2121"),
    ]

    operations = [
        migrations.AddField(
            model_name="community",
            name="listed",
            field=models.BooleanField(
                default=True,
                help_text="Community is visible to non-members in Local Network.",
            ),
        ),
        migrations.AddField(
            model_name="historicalcommunity",
            name="listed",
            field=models.BooleanField(
                default=True,
                help_text="Community is visible to non-members in Local Network.",
            ),
        ),
    ]
