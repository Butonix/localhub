# Generated by Django 3.0.4 on 2020-03-26 00:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("private_messages", "0012_auto_20200301_1050"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="recipient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]