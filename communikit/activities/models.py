# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce
from typing import Callable, List

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel

from taggit.managers import TaggableManager
from taggit.models import Tag

from communikit.comments.models import Comment, CommentAnnotationsQuerySetMixin
from communikit.communities.models import Community
from communikit.core.markdown.fields import MarkdownField
from communikit.core.types import BreadcrumbList
from communikit.core.utils.content_types import get_generic_related_queryset
from communikit.flags.models import Flag, FlagAnnotationsQuerySetMixin
from communikit.likes.models import Like, LikeAnnotationsQuerySetMixin
from communikit.notifications.models import Notification
from communikit.subscriptions.models import Subscription


class ActivityQuerySet(
    CommentAnnotationsQuerySetMixin,
    FlagAnnotationsQuerySetMixin,
    LikeAnnotationsQuerySetMixin,
    models.QuerySet,
):
    def with_common_annotations(
        self, community: Community, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        """
        Combines all common annotations into a single call. Applies annotations
        conditionally e.g. if user is authenticated or not.
        """

        qs = self.with_num_comments()
        if user.is_authenticated:
            qs = (
                qs.with_num_likes().with_has_liked(user).with_has_flagged(user)
            )

            if user.has_perm("communities.moderate_community", community):
                qs = qs.with_is_flagged()
        return qs

    def search(self, search_term: str) -> models.QuerySet:
        if not search_term:
            return self.none()
        query = SearchQuery(search_term)
        return self.annotate(
            rank=SearchRank(models.F("search_document"), query=query)
        ).filter(search_document=query)


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    description = MarkdownField(blank=True)

    tags = TaggableManager()

    search_document = SearchVectorField(null=True, editable=False)

    objects = ActivityQuerySet.as_manager()

    # Note: due to bug in FieldTracker we can't define it in abstract base
    # class and have to define on each subclass.
    # https://github.com/jazzband/django-model-utils/issues/275

    # add following to all Activity subclasses in order to track
    # description for notifications etc.
    # description_tracker = FieldTracker(["description"])

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["owner", "community"]),
        ]
        abstract = True

    @classmethod
    def get_list_url(cls) -> str:
        return reverse(f"{cls._meta.app_label}:list")

    @classmethod
    def get_create_url(cls) -> str:
        return reverse(f"{cls._meta.app_label}:create")

    @classmethod
    def get_breadcrumbs_for_model(cls) -> BreadcrumbList:
        return [
            (settings.HOME_PAGE_URL, _("Home")),
            (cls.get_list_url(), _(cls._meta.verbose_name_plural.title())),
        ]

    def slugify(self) -> str:
        return slugify(smart_text(self), allow_unicode=False)

    def resolve_url(self, view_name: str, *args) -> str:
        return reverse(
            f"{self._meta.app_label}:{view_name}", args=[self.id] + list(args)
        )

    def get_absolute_url(self) -> str:
        return self.resolve_url("detail", self.slugify())

    def get_create_comment_url(self) -> str:
        return self.resolve_url("comment")

    def get_dislike_url(self) -> str:
        return self.resolve_url("dislike")

    def get_like_url(self) -> str:
        return self.resolve_url("like")

    def get_flag_url(self) -> str:
        return self.resolve_url("flag")

    def get_update_url(self) -> str:
        return self.resolve_url("update")

    def get_delete_url(self) -> str:
        return self.resolve_url("delete")

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())

    def get_comments(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Comment)

    def get_flags(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Flag)

    def get_likes(self) -> models.QuerySet:
        return get_generic_related_queryset(self, Like)

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.__class__.get_breadcrumbs_for_model() + [
            (self.get_absolute_url(), truncatechars(smart_text(self), 60))
        ]

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    # set up signal for each subclass
    def make_search_updater(self) -> Callable:
        def on_commit():
            search_vectors = [
                SearchVector(
                    models.Value(text, output_field=models.CharField()),
                    weight=weight,
                )
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_document=reduce(operator.add, search_vectors)
            )

        return on_commit

    def taggit(self, created: bool):
        if created or self.description_tracker.changed():
            hashtags = self.description.extract_hashtags()
            if hashtags:
                self.tags.set(*hashtags, clear=True)
            else:
                self.tags.clear()

    def make_notification(
        self, recipient: settings.AUTH_USER_MODEL, verb: str
    ) -> Notification:
        return Notification(
            content_object=self,
            actor=self.owner,
            community=self.community,
            recipient=recipient,
            verb=verb,
        )

    def notify(self, created: bool) -> List[Notification]:
        notifications: List[Notification] = []
        # notify anyone @mentioned in the description
        if self.description and (
            created or self.description_tracker.changed()
        ):
            notifications += [
                self.make_notification(recipient, "mentioned")
                for recipient in self.community.members.matches_usernames(
                    self.description.extract_mentions()
                ).exclude(pk=self.owner_id)
            ]
            # is anyone subscribing to the hashtags
            # ensure subscriber just has single notification for
            # multiple tags
            hashtags = self.description.extract_hashtags()
            if hashtags:
                tags = Tag.objects.filter(slug__in=hashtags)
                if tags:
                    subscriptions = (
                        Subscription.objects.filter(
                            content_type=ContentType.objects.get_for_model(
                                Tag
                            ),
                            object_id__in=[t.id for t in tags],
                            community=self.community,
                        )
                        .exclude(subscriber=self.owner)
                        .select_related("subscriber")
                        .only("subscriber")
                    )
                    notifications += [
                        self.make_notification(subscriber, "tagged")
                        for subscriber in set(
                            [
                                subscription.subscriber
                                for subscription in subscriptions
                            ]
                        )
                    ]

        # notify all community moderators
        verb = "created" if created else "updated"
        notifications += [
            self.make_notification(recipient, verb)
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        # notify anyone subscribed to this user
        if created:
            subscriptions = (
                Subscription.objects.filter(
                    user=self.owner, community=self.community
                )
                .exclude(subscriber=self.owner)
                .select_related("subscriber")
            )
            notifications += [
                self.make_notification(subscription.subscriber, "created")
                for subscription in subscriptions
            ]

        Notification.objects.bulk_create(notifications)
        return notifications
