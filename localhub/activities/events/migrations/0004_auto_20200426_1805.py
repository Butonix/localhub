# Generated by Django 3.0.5 on 2020-04-26 18:05

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_auto_20200425_0744"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="repeats",
            field=models.CharField(
                blank=True,
                choices=[
                    ("day", "Same time every day"),
                    ("week", "Same day of the week at the same time"),
                    ("month", "First day of the month at the same time"),
                    ("year", "Same date and time every year"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
