# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from localhub.bookmarks.models import Bookmark, BookmarkAnnotationsQuerySetMixin
from localhub.communities.models import Community, Membership
from localhub.db.content_types import (
    get_generic_related_count_subquery,
    get_generic_related_queryset,
)
from localhub.db.search import SearchIndexer, SearchQuerySetMixin
from localhub.db.tracker import Tracker
from localhub.flags.models import Flag, FlagAnnotationsQuerySetMixin
from localhub.likes.models import Like, LikeAnnotationsQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification
from localhub.utils.itertools import takefirst


class CommentAnnotationsQuerySetMixin:
    """
    Adds comment-related annotation methods to a related model
    queryset.
    """

    def with_num_comments(self, community, annotated_name="num_comments"):
        """
        Annotates `num_comments` to the model.
        """
        return self.annotate(
            **{
                annotated_name: get_generic_related_count_subquery(
                    self.model, Comment.objects.for_community(community)
                )
            }
        )


class CommentQuerySet(
    BookmarkAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    SearchQuerySetMixin,
    models.QuerySet,
):
    def for_community(self, community):
        """
        Both community and membership should match.
        """
        return self.filter(
            community=community,
            owner__membership__community=community,
            owner__membership__active=True,
            owner__is_active=True,
        )

    def with_is_parent_owner_member(self, community):
        return self.annotate(
            is_parent_owner_member=models.Exists(
                Membership.objects.filter(
                    member=models.OuterRef("parent__owner__pk"),
                    community=community,
                    active=True,
                )
            )
        )

    def exclude_blocked_users(self, user):

        if user.is_anonymous:
            return self
        return self.exclude(owner__in=user.blocked.all())

    def exclude_deleted(self, user=None):
        qs = self.filter(deleted__isnull=True)
        if user:
            qs = qs | self.filter(owner=user)
        return qs

    def with_is_blocked(self, user):
        if user.is_anonymous:
            return self.annotate(
                is_blocked=models.Value(False, output_field=models.BooleanField())
            )
        return self.annotate(
            is_blocked=models.Exists(
                user.blocked.filter(pk=models.OuterRef("owner_id"))
            )
        )

    def with_common_annotations(self, user, community):
        """
        Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.
        """

        if user.is_authenticated:
            qs = (
                self.with_num_likes()
                .with_has_bookmarked(user)
                .with_has_liked(user)
                .with_has_flagged(user)
                .with_is_blocked(user)
                .with_is_parent_owner_member(community)
            )

            if user.has_perm("community.moderate_community", community):
                qs = qs.with_is_flagged()
            return qs
        return self

    def deleted(self):
        return self.filter(deleted__isnull=False)

    def remove_content_objects(self):
        """
        Sets content object FKs to NULL.
        """
        return self.update(content_type=None, object_id=None)


class Comment(TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    edited = models.DateTimeField(null=True, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)

    content = MarkdownField()

    search_document = SearchVectorField(null=True, editable=False)

    bookmarks = GenericRelation(Bookmark, related_query_name="comment")
    flags = GenericRelation(Flag, related_query_name="comment")
    likes = GenericRelation(Like, related_query_name="comment")
    notifications = GenericRelation(Notification, related_query_name="comment")

    history = HistoricalRecords()
    content_tracker = Tracker(["content"])
    search_indexer = SearchIndexer(("A", "content"))

    objects = CommentQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created", "-created"]),
        ]

    def get_absolute_url(self):
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self):
        """
        Returns absolute URL including the community domain.
        """
        return self.community.resolve_url(self.get_absolute_url())

    def get_notifications(self):
        return get_generic_related_queryset(self, Notification)

    @property
    def _history_user(self):
        return self.editor

    @_history_user.setter
    def _history_user(self, value):
        self.editor = value

    @cached_property
    def first_record(self):
        return self.history.first()

    @cached_property
    def prev_record(self):
        return self.first_record.prev_record if self.first_record else None

    @cached_property
    def changed_fields(self):
        if self.first_record is None or self.prev_record is None:
            return []
        return self.first_record.diff_against(self.prev_record).changed_fields

    def abbreviate(self, length=30):
        text = " ".join(self.content.plaintext().splitlines())
        return truncatechars(text, length)

    def get_bookmarks(self):
        return Bookmark.objects.filter(comment=self)

    def get_flags(self):
        return Flag.objects.filter(comment=self)

    def get_likes(self):
        return Like.objects.filter(comment=self)

    def soft_delete(self):
        self.deleted = timezone.now()
        self.save(update_fields=["deleted"])

        self.get_likes().delete()
        self.get_flags().delete()
        self.get_notifications().delete()

    def make_notification(self, verb, recipient, actor=None):
        return Notification(
            content_object=self,
            recipient=recipient,
            actor=actor or self.owner,
            community=self.community,
            verb=verb,
        )

    def notify_mentioned(self, recipients):
        return [
            self.make_notification("mention", recipient)
            for recipient in recipients.matches_usernames(
                self.content.extract_mentions()
            ).exclude(pk=self.owner_id)
        ]

    def get_notification_recipients(self):
        return self.community.members.exclude(blocked=self.owner)

    @dispatch
    def notify_on_create(self):
        notifications = []
        recipients = self.get_notification_recipients()
        notifications += self.notify_mentioned(recipients)

        # notify the activity owner
        if self.owner_id != self.content_object.owner_id:
            notifications += [
                self.make_notification("new_comment", self.content_object.owner)
            ]

        # notify the person being replied to

        if self.parent:
            notifications += [self.make_notification("reply", self.parent.owner)]

        # notify anyone who has commented on this post, excluding
        # this comment owner and parent owner
        other_commentors = (
            recipients.filter(comment__in=self.content_object.get_comments())
            .exclude(pk__in=(self.owner_id, self.content_object.owner_id))
            .distinct()
        )
        if self.parent:
            other_commentors = other_commentors.exclude(pk=self.parent.owner.id)

        notifications += [
            self.make_notification("new_sibling", commentor)
            for commentor in other_commentors
        ]
        notifications += [
            self.make_notification("followed_user", follower)
            for follower in recipients.filter(following=self.owner)
            .exclude(pk__in=other_commentors)
            .distinct()
        ]
        return takefirst(notifications, lambda n: n.recipient)

    @dispatch
    def notify_on_update(self):
        notifications = []
        if not self.content_tracker.changed():
            return notifications

        recipients = self.get_notification_recipients()
        notifications += self.notify_mentioned(recipients)
        return takefirst(notifications, lambda n: n.recipient)

    @dispatch
    def notify_on_delete(self, moderator):
        return self.make_notification("delete", self.owner, moderator)
