# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("invites", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="invite",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterUniqueTogether(
            name="invite",
            unique_together={("email", "community")},
        ),
    ]
