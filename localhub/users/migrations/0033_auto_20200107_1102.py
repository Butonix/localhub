# Generated by Django 2.2.9 on 2020-01-07 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_user_default_timezone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='email_preferences',
            new_name='notification_preferences',
        ),
    ]