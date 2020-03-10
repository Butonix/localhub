# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.notifications.models import Notification

from ..factories import UserFactory
from ..notifications import send_user_notification_email

pytestmark = pytest.mark.django_db


class TestSendUserNotificationEmail:
    def test_send_notification(self, community, mailoutbox):
        follower = UserFactory()
        followed = UserFactory()

        notification = Notification.objects.create(
            content_object=followed,
            community=community,
            actor=follower,
            recipient=followed,
            verb="new_follower",
        )

        send_user_notification_email(followed, notification)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [followed.email]
