# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List

from django.test.client import Client
from django.urls import reverse

from localite.communities.models import Membership
from localite.messageboard.models import MessageRecipient
from localite.messageboard.tests.factories import (
    MessageFactory,
    MessageRecipientFactory,
)
from localite.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestMessageRecipientListView:
    def test_get(self, client: Client, member: Membership):
        message = MessageFactory(community=member.community)
        MessageRecipientFactory(message=message, recipient=member.member)
        response = client.get(reverse("messageboard:message_recipient_list"))
        assert len(response.context["object_list"]) == 1


class TestMessageRecipientDetailView:
    def test_get(self, client: Client, member: Membership):
        message = MessageFactory(community=member.community)
        recipient = MessageRecipientFactory(
            message=message, recipient=member.member
        )
        response = client.get(recipient.get_absolute_url())
        assert response.context["object"] == recipient


class TestMessageRecipientDeleteView:
    def test_get(self, client: Client, member: Membership):
        message = MessageFactory(community=member.community)
        recipient = MessageRecipientFactory(
            message=message, recipient=member.member
        )
        response = client.get(
            reverse(
                "messageboard:message_recipient_delete", args=[recipient.id]
            )
        )
        assert response.context["object"] == recipient

    def test_delete(self, client: Client, member: Membership):
        message = MessageFactory(community=member.community)
        recipient = MessageRecipientFactory(
            message=message, recipient=member.member
        )
        response = client.delete(
            reverse(
                "messageboard:message_recipient_delete", args=[recipient.id]
            )
        )
        assert response.url == reverse("messageboard:message_recipient_list")
        assert not MessageRecipient.objects.exists()


class TestMessageListView:
    def test_get(self, client: Client, member: Membership):
        MessageFactory(community=member.community, sender=member.member)
        response = client.get(reverse("messageboard:message_list"))
        assert len(response.context["object_list"]) == 1


class TestMessageDetailView:
    def test_get(self, client: Client, member: Membership):
        user = UserFactory()
        message = MessageFactory(
            community=member.community, sender=member.member
        )
        MessageRecipientFactory(message=message, recipient=user)
        response = client.get(message.get_absolute_url())
        assert len(response.context["recipients"]) == 1


class TestMessageCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("messageboard:message_create"))
        assert response.status_code == 200

    def test_get_reply(self, client: Client, member: Membership):
        message = MessageFactory(community=member.community)
        MessageRecipientFactory(recipient=member.member, message=message)
        response = client.get(
            reverse("messageboard:message_create_reply", args=[message.id])
        )
        assert (
            response.context["form"].initial["subject"]
            == f"RE: {message.subject}"
        )
        assert (
            response.context["form"].initial["individuals"]
            == f"@{message.sender.username}"
        )

    def test_get_pm(self, client: Client, member: Membership):
        user = UserFactory()
        response = client.get(
            reverse("messageboard:message_create_pm", args=[user.username])
        )
        assert (
            response.context["form"].initial["individuals"]
            == f"@{user.username}"
        )

    def test_post_no_recipients(self, client: Client, member: Membership):
        response = client.post(
            reverse("messageboard:message_create"),
            {"subject": "test", "message": "test", "groups": "moderators"},
        )
        assert response.status_code == 200

    def test_post_with_recipients(
        self, client: Client, member: Membership, mailoutbox: List
    ):
        user = UserFactory()
        Membership.objects.create(
            member=user,
            community=member.community,
            role=Membership.ROLES.moderator,
        )
        response = client.post(
            reverse("messageboard:message_create"),
            {"subject": "test", "message": "test", "groups": "moderators"},
        )
        assert response.url == reverse("messageboard:message_list")
        assert MessageRecipient.objects.count() == 1
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [user.email]
