# Generated by Django 3.0.5 on 2020-04-08 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0009_auto_20200407_2251'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpoll',
            name='allow_voting',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='allow_voting',
            field=models.BooleanField(default=True),
        ),
    ]
