# Generated by Django 2.2.4 on 2019-08-06 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0024_auto_20190804_1324"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="show_embedded_content",
            field=models.BooleanField(default=False),
        ),
    ]
