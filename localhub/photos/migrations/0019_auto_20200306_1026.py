# Generated by Django 3.0.3 on 2020-03-06 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0018_auto_20200221_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalphoto',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='photo',
            name='is_pinned',
            field=models.BooleanField(default=False),
        ),
    ]