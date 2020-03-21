# Generated by Django 3.0.4 on 2020-03-21 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('join_requests', '0006_auto_20200211_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joinrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], db_index=True, default='pending', max_length=100),
        ),
    ]