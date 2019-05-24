# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import factory
import pytest

from django.db.models import signals

from communikit.communities.models import Community, Membership
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, community: Community):
        moderator = UserFactory()
        mentioned = UserFactory(username="danjac")

        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )
        Membership.objects.create(
            member=mentioned, community=community, role=Membership.ROLES.member
        )

        post = PostFactory(community=community, description="hello @danjac")
        notifications = post.notify(created=True)

        assert notifications[0].recipient == mentioned
        assert notifications[0].verb == "mentioned"

        assert notifications[1].recipient == moderator
        assert notifications[1].verb == "created"

        # ensure saved to db
        assert post.notifications.count() == 2

        # change the description and remove the mention
        post.description = "hello!"
        post.save()

        notifications = post.notify(created=False)

        assert notifications[0].recipient == moderator
        assert notifications[0].verb == "updated"

        assert post.notifications.count() == 3
