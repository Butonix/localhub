# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("join_requests", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="joinrequest",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddIndex(
            model_name="joinrequest",
            index=models.Index(fields=["status"], name="join_reques_status_703ef1_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="joinrequest", unique_together={("community", "sender")},
        ),
    ]
