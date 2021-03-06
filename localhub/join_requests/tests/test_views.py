# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.users.factories import UserFactory

# Local
from ..factories import JoinRequestFactory
from ..models import JoinRequest

pytestmark = pytest.mark.django_db


class TestJoinRequestListView:
    def test_get(self, client, admin):
        JoinRequestFactory.create_batch(3, community=admin.community)
        response = client.get(reverse("join_requests:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3


class TestJoinRequestDetailView:
    def test_get(self, client, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.get(join_request.get_absolute_url())
        assert response.status_code == 200


class TestJoinRequestDeleteView:
    def test_post_if_admin(self, client, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:delete", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        assert JoinRequest.objects.count() == 0

    def test_post_if_sender_no_other_requests(self, client, join_request, login_user):
        response = client.post(reverse("join_requests:delete", args=[join_request.id]))
        assert response.url == settings.HOME_PAGE_URL
        assert JoinRequest.objects.count() == 0

    def test_post_if_sender_has_other_requests(self, client, join_request, login_user):
        JoinRequestFactory(sender=login_user)
        response = client.post(reverse("join_requests:delete", args=[join_request.id]))
        assert response.url == reverse("join_requests:sent_list")
        assert JoinRequest.objects.count() == 1


class TestJoinRequestCreateView:
    def test_get(self, client, login_user, community):
        assert client.get(reverse("join_requests:create")).status_code == 200

    def test_post(self, client, mailoutbox, login_user, community):

        admin = UserFactory()
        Membership.objects.create(
            community=community, member=admin, role=Membership.Role.ADMIN
        )
        response = client.post(reverse("join_requests:create"))
        assert response.url == settings.HOME_PAGE_URL
        join_request = JoinRequest.objects.get()
        assert join_request.sender == login_user
        assert join_request.community == community
        mail = mailoutbox[0]
        assert mail.to == [admin.email]


class TestJoinRequestAcceptView:
    def test_post(self, client, mailoutbox, admin, send_webpush_mock):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:accept", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_accepted()
        assert Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]
        other_member_mail = mailoutbox[1]
        assert other_member_mail.to == [admin.member.email]

    def test_post_if_already_member(self, client, mailoutbox, admin, send_webpush_mock):
        join_request = JoinRequestFactory(community=admin.community)
        MembershipFactory(member=join_request.sender, community=join_request.community)
        response = client.post(reverse("join_requests:accept", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert not join_request.is_accepted()
        assert Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        assert len(mailoutbox) == 0


class TestJoinRequestRejectView:
    def test_post(self, client, mailoutbox, admin):
        join_request = JoinRequestFactory(community=admin.community)
        response = client.post(reverse("join_requests:reject", args=[join_request.id]))
        assert response.url == reverse("join_requests:list")
        join_request.refresh_from_db()
        assert join_request.is_rejected()
        assert not Membership.objects.filter(
            member=join_request.sender, community=admin.community
        ).exists()
        mail = mailoutbox[0]
        assert mail.to == [join_request.sender.email]


class TestSentJoinRequestListView:
    def test_get(self, client, join_request):
        response = client.get(reverse("join_requests:sent_list"))
        assert response.status_code == 200
        assert join_request in response.context["object_list"]
