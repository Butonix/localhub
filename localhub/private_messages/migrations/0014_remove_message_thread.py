# Generated by Django 3.0.4 on 2020-03-31 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('private_messages', '0013_auto_20200326_0026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='thread',
        ),
    ]
