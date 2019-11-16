# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.users.factories import UserFactory

from ..factories import MessageFactory
from ..notifications import send_message_email

pytestmark = pytest.mark.django_db


class TestSendMessageEmail:
    def test_if_enabled(self, mailoutbox):
        user = UserFactory(email_preferences=["new_message"])
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]

    def test_if_disabled(self, mailoutbox):
        user = UserFactory(email_preferences=[])
        message = MessageFactory(recipient=user)
        send_message_email(message)
        assert len(mailoutbox) == 0
