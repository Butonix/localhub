# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("comments", "0001_initial"),
        ("communities", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="community",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="communities.Community"
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="contenttypes.ContentType",
            ),
        ),
    ]
