# Generated by Django 3.0.5 on 2020-04-23 03:12

import django.contrib.postgres.search
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields

import localhub.apps.hashtags.fields
import localhub.apps.users.fields
import localhub.common.markdown.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("communities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(max_length=180)),
            ],
        ),
        migrations.CreateModel(
            name="Poll",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                (
                    "hashtags",
                    localhub.apps.hashtags.fields.HashtagsField(
                        blank=True, max_length=300
                    ),
                ),
                (
                    "mentions",
                    localhub.apps.users.fields.MentionsField(
                        blank=True, max_length=300
                    ),
                ),
                (
                    "description",
                    localhub.common.markdown.fields.MarkdownField(blank=True),
                ),
                ("allow_comments", models.BooleanField(default=True)),
                ("is_reshare", models.BooleanField(default=False)),
                ("is_pinned", models.BooleanField(default=False)),
                ("edited", models.DateTimeField(blank=True, null=True)),
                ("published", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "search_document",
                    django.contrib.postgres.search.SearchVectorField(
                        editable=False, null=True
                    ),
                ),
                ("allow_voting", models.BooleanField(default=True)),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="communities.Community",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
