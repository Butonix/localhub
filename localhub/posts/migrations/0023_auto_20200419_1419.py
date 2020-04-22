# Generated by Django 3.0.5 on 2020-04-19 14:19

from django.db import migrations

import localhub.hashtags.fields


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0022_auto_20200419_1330"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalpost",
            name="additional_tags",
            field=localhub.hashtags.fields.HashtagsField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name="post",
            name="additional_tags",
            field=localhub.hashtags.fields.HashtagsField(blank=True, max_length=300),
        ),
    ]