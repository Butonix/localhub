import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.comments.models import Comment
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.content.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestCommentCreate:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("comments:create", args=[post.id]), {"content": "test"}
        )
        assert response.url == post.get_absolute_url()
        comment = post.comment_set.get()
        assert comment.author == member.member


class TestCommentDetail:
    def test_get(self, client: Client, comment: Comment):
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.post.community.domain,
        )
        assert response.status_code == 200


class TestCommentUpdate:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.get(reverse("comments:update", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.post(
            reverse("comments:update", args=[comment.id]),
            {"content": "new content"},
        )
        assert response.url == post.get_absolute_url()
        comment.refresh_from_db()
        assert comment.content == "new content"


class TestCommentDelete:
    def test_delete(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.delete(reverse("comments:delete", args=[comment.id]))
        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0

    def test_delete_ajax(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.delete(
            reverse("comments:delete", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Comment.objects.count() == 0
