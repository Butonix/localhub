# Generated by Django 2.2.2 on 2019-08-01 06:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0008_auto_20190729_2118"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpost",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="posts.Post",
            ),
        ),
        migrations.AddField(
            model_name="historicalpost",
            name="reshared",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="post",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reshares",
                to="posts.Post",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="reshared",
            field=models.BooleanField(default=False),
        ),
    ]
