import pytest

from django.conf import settings

from communikit.activities.rules import (
    is_activity_community_moderator,
    is_editor,
    is_owner,
)
from communikit.communities.models import Community, Membership
from communikit.posts.models import Post
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestIsOwner:
    def test_is_owner(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory(owner=user)
        assert is_owner.test(user, post)
        assert is_editor.test(user, post)

    def test_is_not_owner(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory()
        assert not is_owner.test(user, post)
        assert not is_editor.test(user, post)


class TestIsPostCommunityModerator:
    def test_is_moderator(self, moderator: settings.AUTH_USER_MODEL):
        post = PostFactory(community=moderator.community)
        assert is_activity_community_moderator.test(moderator.member, post)
        assert is_editor(moderator.member, post)

    def test_is_not_moderator(self, user: settings.AUTH_USER_MODEL):
        post = PostFactory()
        assert not is_activity_community_moderator.test(user, post)
        assert not is_editor(user, post)


class TestPermissions:
    def test_owner_can_like_activity(self, post: Post):
        assert not post.owner.has_perm("activities.like_activity", post)

    def test_member_can_like_activity(self, member: Membership):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.like_activity", post)

    def test_owner_can_flag_activity(self, post: Post):
        assert not post.owner.has_perm("activities.flag_activity", post)

    def test_member_can_flag_activity(self, member: Membership):
        post = PostFactory(community=member.community)
        assert member.member.has_perm("activities.flag_activity", post)

    def test_member_can_create_activity(self, member: Membership):
        assert member.member.has_perm(
            "activities.create_activity", member.community
        )

    def test_non_member_can_create_activity(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ):
        assert not user.has_perm("activities.create_activity", community)

    def test_owner_can_edit_or_delete_activity(
        self, user: settings.AUTH_USER_MODEL
    ):
        post = PostFactory(owner=user)
        assert user.has_perm("activities.change_activity", post)
        assert user.has_perm("activities.delete_activity", post)

    def test_non_owner_can_edit_or_delete_activity(
        self, user: settings.AUTH_USER_MODEL
    ):
        post = PostFactory()
        assert not user.has_perm("activities.change_activity", post)
        assert not user.has_perm("activities.delete_activity", post)

    def test_moderator_can_edit_or_delete_activity(
        self, moderator: settings.AUTH_USER_MODEL
    ):
        post = PostFactory(community=moderator.community)

        assert moderator.member.has_perm("activities.change_activity", post)
        assert moderator.member.has_perm("activities.delete_activity", post)
