# Generated by Django 2.2.2 on 2019-07-20 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0005_photo_editor"),
    ]

    operations = [
        migrations.RemoveField(model_name="photo", name="editor",),
    ]
