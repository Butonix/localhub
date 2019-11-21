# Generated by Django 2.2.7 on 2019-11-21 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20191107_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpost',
            name='published',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='published',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['published', '-published'], name='posts_post_publish_0f09a8_idx'),
        ),
    ]
