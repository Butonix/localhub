# Generated by Django 3.0.3 on 2020-02-21 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_auto_20191121_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='edited',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalevent',
            name='edited',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
