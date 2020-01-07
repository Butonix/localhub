# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from unittest import mock

import pytest
from pywebpush import WebPushException

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Community
from localhub.users.factories import UserFactory

from ..factories import NotificationFactory
from ..models import Notification, PushSubscription

pytestmark = pytest.mark.django_db


class TestNotificationManager:
    def test_for_community(self, community: Community):

        notification = NotificationFactory(
            community=community, actor=MembershipFactory(community=community).member,
        )
        NotificationFactory(actor=MembershipFactory(community=community).member)
        NotificationFactory(
            actor=MembershipFactory(community=community, active=False).member
        )
        NotificationFactory(
            actor=MembershipFactory(community=CommunityFactory(), active=True).member
        )
        NotificationFactory(community=community)
        NotificationFactory()

        qs = Notification.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == notification

    def test_bulk_create_if_prefs_has_pref(self, post):
        user = UserFactory(notification_preferences=["reshare"])
        notification = post.make_notification(user, "reshare")
        created = Notification.objects.bulk_create_if_prefs([notification])
        assert created[0] == notification

    def test_bulk_create_if_prefs_does_not_have_pref(self, post):
        user = UserFactory(notification_preferences=[])
        notification = post.make_notification(user, "reshare")
        created = Notification.objects.bulk_create_if_prefs([notification])
        assert not created


class TestPushSubscriptionModel:
    def test_push_if_ok(self, member, send_notification_webpush_mock):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        assert sub.push(payload)
        assert send_notification_webpush_mock.called_with(
            {
                "endpoint": sub.endpoint,
                "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
            },
            payload,
            ttf=0,
        )

        assert PushSubscription.objects.exists()

    def test_push_if_timeout(self, member):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        e = WebPushException("BOOM", response=mock.Mock(status_code=410))

        with mock.patch("localhub.notifications.models.webpush", side_effect=e):
            assert not sub.push(payload)

        assert not PushSubscription.objects.exists()
