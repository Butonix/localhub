# Generated by Django 2.2.4 on 2019-08-30 12:23

from django.db import migrations, models

import localhub.core.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_auto_20190825_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_preferences',
            field=localhub.core.db.fields.ChoiceArrayField(base_field=models.CharField(choices=[('new_message', 'I receive a direct message'), ('new_follower', 'Someone starts following me'), ('new_member', 'Someone joins a community I belong to'), ('new_comment', 'Someone comments on my post, event or photo'), ('new_sibling_comment', "Someone comments on a post, event or photo I've also commented on"), ('reshare', 'Someone has reshared my post, event or photo'), ('mention', 'I am @mentioned in a post, event, photo or comment'), ('moderator_delete', 'A moderator deletes my post, event, photo or comment'), ('moderator_edit', 'A moderator edits my post, event, photo or comment'), ('like', 'Someone likes my post, event, photo or comment'), ('new_followed_user_post', "Someone I'm following submits a post, event or photo"), ('replied_to_comment', 'Someone replies to my comment'), ('new_followed_user_comment', "Someone I'm following submits a comment"), ('new_followed_tag_post', "A post, event or photo is submitted containing tags I'm following"), ('flag', 'A user has flagged a comment, post, event or photo (moderators only)'), ('moderator_review_request', 'A user has a new comment, post, event or photo for you to review (moderators only)')], max_length=30), blank=True, default=list, size=None),
        ),
    ]
