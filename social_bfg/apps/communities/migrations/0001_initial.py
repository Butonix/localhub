# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

# Third Party Libraries
import model_utils.fields
import sorl.thumbnail.fields

# Social-BFG
import social_bfg.markdown.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Community",
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
                (
                    "domain",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="This is not a valid domain",
                                regex="([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)",
                            )
                        ],
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "logo",
                    sorl.thumbnail.fields.ImageField(
                        blank=True, null=True, upload_to="logo"
                    ),
                ),
                ("tagline", models.TextField(blank=True)),
                ("intro", social_bfg.markdown.fields.MarkdownField(blank=True)),
                ("description", social_bfg.markdown.fields.MarkdownField(blank=True),),
                ("terms", social_bfg.markdown.fields.MarkdownField(blank=True)),
                ("content_warning_tags", models.TextField(blank=True, default="#nsfw")),
                (
                    "email_domain",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="This is not a valid domain",
                                regex="([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)",
                            )
                        ],
                    ),
                ),
                (
                    "google_tracking_id",
                    models.CharField(blank=True, max_length=30, null=True),
                ),
                ("active", models.BooleanField(default=True)),
                ("public", models.BooleanField(default=True)),
                ("allow_join_requests", models.BooleanField(default=True)),
                ("blacklisted_email_domains", models.TextField(blank=True)),
                ("blacklisted_email_addresses", models.TextField(blank=True)),
            ],
            options={"verbose_name_plural": "Communities",},
        ),
        migrations.CreateModel(
            name="Membership",
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
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("member", "Member"),
                            ("moderator", "Moderator"),
                            ("admin", "Admin"),
                        ],
                        db_index=True,
                        default="member",
                        max_length=9,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="communities.Community",
                    ),
                ),
            ],
        ),
    ]
