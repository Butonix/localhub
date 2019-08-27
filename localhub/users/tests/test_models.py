# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress

from localhub.communities.models import Membership, RequestCommunity
from localhub.communities.tests.factories import MembershipFactory
from localhub.notifications.models import Notification
from localhub.posts.tests.factories import PostFactory
from localhub.private_messages.tests.factories import MessageFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserManager:
    def test_create_user(self):

        user = get_user_model().objects.create_user(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.check_password("t3ZtP4s31")

    def test_active(self, community):
        Membership.objects.create(member=UserFactory(), community=community)
        assert get_user_model().objects.active(community).exists()

    def test_active_if_not_member(self, community):
        UserFactory()
        assert not get_user_model().objects.active(community).exists()

    def test_active_if_not_active_member(self, community):
        Membership.objects.create(
            member=UserFactory(), community=community, active=False
        )
        assert not get_user_model().objects.active(community).exists()

    def test_active_if_not_active(self, community):
        Membership.objects.create(
            member=UserFactory(is_active=False), community=community
        )
        assert not get_user_model().objects.active(community).exists()

    def test_create_superuser(self):

        user = get_user_model().objects.create_superuser(
            username="tester", email="tester@gmail.com", password="t3ZtP4s31"
        )
        assert user.is_superuser
        assert user.is_staff

    def test_for_email_matching_email_field(self):

        user = UserFactory(email="test@gmail.com")
        assert (
            get_user_model().objects.for_email("test@gmail.com").first()
            == user
        )

    def test_for_email_matching_email_address_instance(self):

        user = UserFactory()
        EmailAddress.objects.create(user=user, email="test@gmail.com")
        assert (
            get_user_model().objects.for_email("test@gmail.com").first()
            == user
        )

    def test_matches_usernames(self):
        user_1 = UserFactory(username="first")
        user_2 = UserFactory(username="second")
        user_3 = UserFactory(username="third")

        names = ["second", "FIRST", "SEconD"]  # duplicate

        users = get_user_model().objects.matches_usernames(names)
        assert len(users) == 2
        assert user_1 in users
        assert user_2 in users
        assert user_3 not in users

        # check empty set returns no results
        assert get_user_model().objects.matches_usernames([]).count() == 0

    def test_is_following(self, user):

        followed = UserFactory()
        UserFactory()

        user.following.add(followed)

        users = get_user_model().objects.all().with_is_following(user)

        for user in users:
            if user == followed:
                assert user.is_following
            else:
                assert not user.is_following

    def test_is_blocked(self, user):

        blocked = UserFactory()
        UserFactory()

        user.blocked.add(blocked)

        users = get_user_model().objects.all().with_is_blocked(user)

        for user in users:
            if user == blocked:
                assert user.is_blocked
            else:
                assert not user.is_blocked


class TestUserModel:
    def test_get_absolute_url(self, user):
        assert user.get_absolute_url() == f"/people/{user.username}/"

    def test_has_email_pref(self):
        user = UserFactory(email_preferences=["messages"])
        assert user.has_email_pref("messages")

    def test_does_not_have_email_pref(self):
        user = UserFactory()
        assert not user.has_email_pref("messages")

    def test_has_role(self, moderator):
        assert moderator.member.has_role(
            moderator.community, Membership.ROLES.moderator
        )

    def test_does_not_have_role(self, member):
        assert not member.member.has_role(
            member.community, Membership.ROLES.moderator
        )

    def test_get_unread_notification_count(self, user, community):
        Notification.objects.create(
            verb="mention",
            recipient=user,
            community=community,
            content_object=PostFactory(),
            actor=UserFactory(),
        )
        assert user.get_unread_notification_count(community) == 1

    def test_get_unread_notification_count_if_community_id_none(
        self, user, req_factory
    ):
        req = req_factory.get("/")
        assert (
            user.get_unread_notification_count(
                RequestCommunity(req, "example.com", "example.com")
            )
            == 0
        )

    def test_get_unread_message_count(self):
        message = MessageFactory()
        assert (
            message.recipient.get_unread_message_count(message.community) == 1
        )

    def test_get_unread_message_count_if_community_id_none(
        self, user, req_factory
    ):
        req = req_factory.get("/")
        assert (
            user.get_unread_message_count(
                RequestCommunity(req, "example.com", "example.com")
            )
            == 0
        )

    def test_notify_on_join(self, member):
        other_member = MembershipFactory(community=member.community).member
        notifications = member.member.notify_on_join(member.community)
        assert len(notifications) == 1
        assert notifications[0].recipient == other_member
        assert notifications[0].content_object == member.member
        assert notifications[0].actor == member.member
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_member"

    def test_notify_on_follow(self, member):
        follower = MembershipFactory(community=member.community).member
        notifications = follower.notify_on_follow(
            member.member, member.community
        )
        assert len(notifications) == 1
        assert notifications[0].recipient == member.member
        assert notifications[0].content_object == follower
        assert notifications[0].actor == follower
        assert notifications[0].community == member.community
        assert notifications[0].verb == "new_follower"
