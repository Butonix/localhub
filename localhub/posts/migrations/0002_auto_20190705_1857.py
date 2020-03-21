# Generated by Django 2.2.2 on 2019-07-05 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="post",
            index=models.Index(
                fields=["owner", "community"], name="posts_post_owner_i_f616f0_idx"
            ),
        ),
    ]
