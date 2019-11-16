# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest
from django.contrib.auth.models import AnonymousUser

from ..templatetags.communities_tags import get_available_community_count
from .factories import CommunityFactory, MembershipFactory

pytestmark = pytest.mark.django_db


class TestGetAvailableCommunityCount:
    def test_anonymous(self, community):
        assert get_available_community_count({}, AnonymousUser()) == 0

    def test_authenticated(self, member):
        CommunityFactory(listed=False)
        MembershipFactory(member=member.member).community
        assert get_available_community_count({}, member.member) == 2
