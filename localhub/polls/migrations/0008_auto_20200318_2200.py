# Generated by Django 3.0.4 on 2020-03-18 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0007_auto_20200317_2242"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpoll",
            name="additional_tags",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="poll",
            name="additional_tags",
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
