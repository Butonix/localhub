# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("communities", "0002_auto_20200423_0312"),
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pushsubscription",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="actor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="community",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="communities.Community"
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.ContentType",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="recipient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="pushsubscription",
            constraint=models.UniqueConstraint(
                fields=("user", "auth", "p256dh", "community"),
                name="unique_push_notification",
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["content_type", "object_id", "created", "-created", "is_read"],
                name="notificatio_content_b064c5_idx",
            ),
        ),
    ]