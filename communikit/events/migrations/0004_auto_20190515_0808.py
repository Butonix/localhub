# Generated by Django 2.2 on 2019-05-15 08:08

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20190514_2153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
        migrations.AddField(
            model_name='event',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='locality',
            field=models.CharField(blank=True, max_length=200, verbose_name='City or town'),
        ),
        migrations.AddField(
            model_name='event',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='event',
            name='region',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='event',
            name='street_address',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
