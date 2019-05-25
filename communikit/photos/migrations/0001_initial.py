# Generated by Django 2.2 on 2019-05-25 15:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('activities', '0003_auto_20190519_1950'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('activity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='activities.Activity')),
                ('title', models.CharField(max_length=300)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='photos/')),
                ('tags', models.CharField(blank=True, max_length=300)),
            ],
            options={
                'abstract': False,
            },
            bases=('activities.activity',),
        ),
        migrations.CreateModel(
            name='PhotoNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('verb', models.CharField(max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='photos.Photo')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
