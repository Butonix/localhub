# Generated by Django 3.0.5 on 2020-04-23 03:12

import django.contrib.postgres.search
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields
import sorl.thumbnail.fields

import localhub.apps.users.fields
import localhub.common.markdown.fields
import localhub.hashtags.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("communities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Photo",
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
                    localhub.hashtags.fields.HashtagsField(blank=True, max_length=300),
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
                (
                    "image",
                    sorl.thumbnail.fields.ImageField(
                        help_text="For best results, photos should be no larger than 1MB. If the image is too large it will not be accepted.",
                        upload_to="photos",
                        verbose_name="Photo",
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("artist", models.CharField(blank=True, max_length=100)),
                (
                    "original_url",
                    models.URLField(blank=True, max_length=500, null=True),
                ),
                (
                    "cc_license",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("by", "Attribution"),
                            ("by-sa", "Attribution ShareAlike"),
                            ("by-nd", "Attribution NoDerivs"),
                            ("by-nc", "Attribution NonCommercial"),
                            ("by-nc-sa", "Attribution NonCommercial ShareAlike"),
                            ("by-nc-nd", "Attribution NonCommercial NoDerivs"),
                        ],
                        max_length=10,
                        null=True,
                        verbose_name="Creative Commons license",
                    ),
                ),
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
