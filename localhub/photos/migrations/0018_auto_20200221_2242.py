# Generated by Django 3.0.3 on 2020-02-21 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0017_auto_20200202_1019"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalphoto",
            name="edited",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="photo",
            name="edited",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
