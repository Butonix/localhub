# Generated by Django 3.0.3 on 2020-03-06 17:00

from django.db import migrations, models

import localhub.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0035_auto_20200305_1456"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="home_page_filters",
            field=localhub.db.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("users", "Limited to just content from people I'm following"),
                        ("tags", "Limited to just tags I'm following"),
                    ],
                    max_length=12,
                ),
                blank=True,
                default=list,
                size=None,
                verbose_name="Stream Filters",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="notification_preferences",
            field=localhub.db.fields.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("new_message", "I have received a direct message"),
                        ("new_follower", "Someone has started following me"),
                        ("new_member", "Someone has joined a community I belong to"),
                        (
                            "new_comment",
                            "Someone has commented on one of my activities",
                        ),
                        (
                            "replied_to_comment",
                            "Someone has replied to one of my comments",
                        ),
                        (
                            "new_sibling_comment",
                            "Someone has commented on an activity I've also commented on",
                        ),
                        ("like", "Someone has liked one of my activities or comments"),
                        ("reshare", "Someone has reshared one of my activities"),
                        ("mention", "I have been @mentioned in an activity or comment"),
                        (
                            "moderator_delete",
                            "A moderator has deleted one of my activities or comments",
                        ),
                        (
                            "moderator_edit",
                            "A moderator has edited one of my activities or comments",
                        ),
                        (
                            "new_followed_user_post",
                            "Someone I'm following has posted an activity",
                        ),
                        (
                            "new_followed_user_comment",
                            "Someone I'm following has posted a comment",
                        ),
                        (
                            "new_followed_tag_post",
                            "An activity has been posted containing tags I'm following",
                        ),
                        (
                            "flag",
                            "A user has flagged content they are concerned about (community moderators only)",
                        ),
                        (
                            "moderator_review_request",
                            "A user has posted content for me to review (community moderators only)",
                        ),
                    ],
                    max_length=30,
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
