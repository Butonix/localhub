# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("bookmarks", "0001_initial"),
        ("communities", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bookmark",
            name="community",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="communities.Community",
            ),
        ),
        migrations.AddField(
            model_name="bookmark",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.ContentType",
            ),
        ),
    ]
