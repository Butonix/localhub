# Generated by Django 2.2.4 on 2019-08-04 13:24

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0023_auto_20190803_1611"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="search_document",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_document"], name="users_user_search__568be7_gin"
            ),
        ),
    ]
