import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.comments.models import Comment
from communikit.communities.models import Community, Membership
from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member: Membership) -> Post:
    return PostFactory(author=member.member, community=member.community)


class TestPostCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("content:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("content:create"), {"title": "test", "description": "test"}
        )
        assert response.url == reverse("content:list")
        post = Post.objects.get()
        assert post.author == member.member
        assert post.community == member.community


class TestPostListView:
    def test_get(self, community: Community, client: Client):
        PostFactory.create_batch(3, community=community)
        response = client.get(reverse("content:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3

    def test_with_comments(self, comment: Comment, client: Client):
        response = client.get(
            reverse("content:list"), HTTP_HOST=comment.post.community.domain
        )

        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
        assert response.context["object_list"][0].num_comments == 1


class TestUpdateView:
    def test_get(self, client: Client, post_for_member: Post):
        response = client.get(
            reverse("content:update", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_post(self, client: Client, post_for_member: Post):
        response = client.post(
            reverse("content:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )
        assert response.url == post_for_member.get_absolute_url()
        post_for_member.refresh_from_db()
        assert post_for_member.title == "UPDATED"


class TestDetailView:
    def test_get(self, client: Client, post: Post):
        response = client.get(
            reverse("content:detail", args=[post.id]),
            HTTP_HOST=post.community.domain,
        )
        assert response.status_code == 200


class TestDeleteView:
    def test_get(self, client: Client, post_for_member: Post):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("content:delete", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client: Client, post_for_member: Post):
        response = client.delete(
            reverse("content:delete", args=[post_for_member.id])
        )
        assert response.url == reverse("content:list")
        assert Post.objects.count() == 0
