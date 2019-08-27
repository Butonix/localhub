import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCommentManager:
    def test_search(self):

        comment = CommentFactory(content="testme")
        other_comment = CommentFactory(content="not found")

        comment.search_indexer.update()
        other_comment.search_indexer.update()

        assert Comment.objects.search("testme").get() == comment

    def test_blocked_users(self, user):

        my_comment = CommentFactory(owner=user)

        first_comment = CommentFactory()
        second_comment = CommentFactory()
        user.blocked.add(first_comment.owner)

        comments = Comment.objects.blocked_users(user).all()
        assert len(comments) == 2
        assert my_comment in comments
        assert second_comment in comments

    def test_For_community(self, community):
        comment = CommentFactory(
            community=community,
            owner=MembershipFactory(community=community).member,
        )
        CommentFactory(owner=MembershipFactory(community=community).member)
        CommentFactory(community=community)
        CommentFactory()
        assert Comment.objects.for_community(community).get() == comment

    def test_with_num_likes(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )

        comment = Comment.objects.with_num_likes().get()
        assert comment.num_likes == 1

    def test_with_has_flagged_if_user_has_not_flagged(self, comment, user):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(UserFactory()).get()
        assert not comment.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, comment, user):
        Flag.objects.create(
            user=user, content_object=comment, community=comment.community
        )
        comment = Comment.objects.with_has_flagged(user).get()
        assert comment.has_flagged

    def test_with_has_liked_if_user_has_not_liked(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(UserFactory()).get()
        assert not comment.has_liked

    def test_with_has_liked_if_user_has_liked(self, comment, user):
        Like.objects.create(
            user=user,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        comment = Comment.objects.with_has_liked(user).get()
        assert comment.has_liked

    def test_with_common_annotations_if_anonymous(self, comment):
        comment = Comment.objects.with_common_annotations(
            comment.community, AnonymousUser()
        ).get()

        assert not hasattr(comment, "num_likes")
        assert not hasattr(comment, "has_liked")
        assert not hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")

    def test_with_common_annotations_if_authenticated(self, comment, user):
        comment = Comment.objects.with_common_annotations(
            comment.community, user
        ).get()

        assert hasattr(comment, "num_likes")
        assert hasattr(comment, "has_liked")
        assert hasattr(comment, "has_flagged")
        assert not hasattr(comment, "is_flagged")


class TestCommentModel:
    def test_notify_on_create(self, community):

        comment_owner = MembershipFactory(community=community).member
        post_owner = MembershipFactory(community=community).member
        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator
        ).member

        mentioned = UserFactory(username="danjac")

        MembershipFactory(member=mentioned, community=community)

        post = PostFactory(owner=post_owner, community=community)

        other_comment = CommentFactory(
            owner=MembershipFactory(community=community).member,
            content_object=post,
        )

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        follower = MembershipFactory(community=community).member
        follower.following.add(comment.owner)

        notifications = comment.notify_on_create()

        assert len(notifications) == 5

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == comment.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == moderator
        assert notifications[1].actor == comment.owner
        assert notifications[1].verb == "moderator_review_request"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == comment.owner
        assert notifications[2].verb == "new_comment"

        assert notifications[3].recipient == other_comment.owner
        assert notifications[3].actor == comment.owner
        assert notifications[3].verb == "new_sibling_comment"

        assert notifications[4].recipient == follower
        assert notifications[4].actor == comment.owner
        assert notifications[4].verb == "new_followed_user_comment"

    def test_notify_on_update(self, community):

        comment_owner = MembershipFactory(community=community).member
        post_owner = MembershipFactory(community=community).member
        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator
        ).member

        post = PostFactory(owner=post_owner, community=community)

        comment = CommentFactory(
            owner=comment_owner,
            community=community,
            content_object=post,
            content="hello @danjac",
        )

        # edit by moderator
        comment.editor = moderator
        comment.content = "edit #1"
        comment.save()

        notifications = comment.notify_on_update()
        assert len(notifications) == 1

        assert notifications[0].recipient == comment.owner
        assert notifications[0].actor == moderator
        assert notifications[0].verb == "moderator_edit"

        # edit by owner
        comment.content = "edit #2"
        comment.editor = comment_owner
        comment.save()

        notifications = comment.notify_on_update()
        assert len(notifications) == 1

        assert notifications[0].recipient == moderator
        assert notifications[0].actor == comment_owner
        assert notifications[0].verb == "moderator_review_request"
