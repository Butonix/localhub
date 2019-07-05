# Generated by Django 2.2.2 on 2019-07-05 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['content_type', 'object_id', 'subscriber'], name='subscriptio_content_65ea15_idx'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('subscriber', 'content_type', 'object_id'), name='unique_subscription'),
        ),
    ]
