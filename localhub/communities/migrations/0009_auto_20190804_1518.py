# Generated by Django 2.2.4 on 2019-08-04 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0008_auto_20190724_2227"),
    ]

    operations = [
        migrations.AddField(
            model_name="community", name="tagline", field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="historicalcommunity",
            name="tagline",
            field=models.TextField(blank=True),
        ),
    ]
