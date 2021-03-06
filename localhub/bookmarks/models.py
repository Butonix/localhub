# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Third Party Libraries
from model_utils.models import TimeStampedModel

# Localhub
from localhub.common.db.generic import (
    get_generic_related_exists,
    get_generic_related_value_subquery,
)
from localhub.common.db.utils import boolean_value
from localhub.communities.models import Community


class BookmarkAnnotationsQuerySetMixin:
    """
    Annotation methods for related model query sets.
    """

    def exists_bookmarks(self, user):
        return get_generic_related_exists(
            self.model, Bookmark.objects.filter(user=user)
        )

    def with_has_bookmarked(self, user, annotated_name="has_bookmarked"):
        """Checks if user has liked the objects, adding `has_liked`
        annotation.

        Args:

            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation name (default: "has_bookmarked")

        Returns:

            QuerySet
        """
        return self.annotate(
            **{
                annotated_name: boolean_value(False)
                if user.is_anonymous
                else self.exists_bookmarks(user)
            }
        )

    def bookmarked(self, user, annotated_name="has_bookmarked"):
        """Filters queryset and returns only those which have been bookmarked.

        Args:

            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation name (default: "has_bookmarked")

        Returns:

            QuerySet
        """
        if user.is_anonymous:
            return self.none()

        return self.filter(self.exists_bookmarks(user)).annotate(
            **{annotated_name: boolean_value(True)}
        )

    def with_bookmarked_timestamp(self, user, annotated_name="bookmarked"):
        """Adds annotated "bookmarked" timestamp to bookmarked items.

        Args:
            user (User): user who has bookmarked the items
            annotated_name (str, optional): annotation timestamp name (default: "bookmarked")

        Returns:
            QuerySet
        """

        if user.is_anonymous:
            return self.none()

        return self.annotate(
            **{
                annotated_name: get_generic_related_value_subquery(
                    self.model,
                    Bookmark.objects.filter(user=user),
                    "created",
                    models.DateTimeField(),
                )
            }
        )


class BookmarkQuerySet(models.QuerySet):
    def for_models(self, *models):
        """
        Returns instances of a Bookmark for a given set of models.
        """
        return self.filter(
            content_type__in=ContentType.objects.get_for_models(*models).values()
        )


class Bookmark(TimeStampedModel):

    community = models.ForeignKey(Community, related_name="+", on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = BookmarkQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_bookmark",
            )
        ]
        indexes = [models.Index(fields=["content_type", "object_id"])]
