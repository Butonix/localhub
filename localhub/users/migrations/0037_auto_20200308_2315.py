# Generated by Django 3.0.3 on 2020-03-08 23:15

from django.db import migrations, models

import localhub.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_auto_20200306_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='home_page_filters',
            field=localhub.db.fields.ChoiceArrayField(base_field=models.CharField(choices=[('users', "Limited to just content from people I'm following"), ('tags', "Limited to just tags I'm following")], max_length=12), blank=True, default=list, size=None, verbose_name='Activity Stream Filters'),
        ),
    ]
