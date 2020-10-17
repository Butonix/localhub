# Generated by Django 3.1.2 on 2020-10-17 19:25

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flags", "0002_auto_20200423_0312"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flag",
            name="reason",
            field=models.CharField(
                choices=[
                    ("spam", "Spam"),
                    ("abuse", "Personal, racial or other abuse"),
                    ("rules", "Breach of community rules"),
                    ("illegal_activity", "Illegal activity"),
                    ("pornography", "Pornography"),
                    ("copyright", "Breach of copyright"),
                    ("fake_news", "Fake news or harmful misinformation"),
                ],
                default="spam",
                max_length=30,
            ),
        ),
    ]
