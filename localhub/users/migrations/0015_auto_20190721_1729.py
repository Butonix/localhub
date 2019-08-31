# Generated by Django 2.2.2 on 2019-07-21 17:29

from django.db import migrations, models
import localhub.common.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20190721_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_preferences',
            field=localhub.common.db.fields.ChoiceArrayField(base_field=models.CharField(choices=[('comments', 'Someone comments on my post'), ('deletes', 'A moderator deletes my post or comment'), ('edits', 'A moderator edits my post or comment'), ('follows', "Someone I'm following creates a post"), ('likes', 'Someone likes my post or comment'), ('joins', 'Someone joins my community'), ('join_requests', 'Someone requests to join my community (ADMINS ONLY)'), ('mentions', 'I am @mentioned in a post or comment'), ('messages', 'I receive a direct message'), ('tags', "A post is created containing tags I'm following"), ('flags', 'Post or comment is flagged (MODERATORS ONLY)'), ('reviews', 'Content to be reviewed (MODERATORS ONLY)'), ('subscribes', 'Someone starts following me')], max_length=12), blank=True, default=list, size=None),
        ),
    ]
