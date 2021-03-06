# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import reverse

# Third Party Libraries
import pytest

# Localhub
from localhub.activities.posts.factories import PostFactory

# Local
from ..factories import FlagFactory
from ..models import Flag

pytestmark = pytest.mark.django_db


class TestFlagListView:
    def test_get(self, client, moderator):
        post = PostFactory(community=moderator.community)
        FlagFactory(
            content_object=post,
            community=moderator.community,
        )
        response = client.get(reverse("flags:list"))
        assert response.status_code == 200


class TestFlagDeleteView:
    def test_post(self, client, moderator):
        post = PostFactory(community=moderator.community)
        flag = FlagFactory(
            content_object=post,
            community=moderator.community,
        )
        response = client.post(reverse("flags:delete", args=[flag.id]))
        assert response.url == post.get_absolute_url()
        assert not Flag.objects.exists()
