# Generated by Django 3.0.5 on 2020-05-02 14:11

# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0002_auto_20200423_0312"),
    ]

    operations = [
        migrations.RemoveField(model_name="community", name="google_tracking_id",),
    ]
