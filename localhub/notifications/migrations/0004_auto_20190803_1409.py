# Generated by Django 2.2.4 on 2019-08-03 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0003_auto_20190705_1857"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="verb",
            field=models.CharField(max_length=30),
        ),
    ]
