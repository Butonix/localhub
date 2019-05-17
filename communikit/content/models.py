import operator

from collections import defaultdict
from functools import reduce
from typing import Set, Callable, List, Dict

from django.conf import settings
from django.core.paginator import Paginator, Page
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.postgres.search import (
    SearchVectorField,
    SearchVector,
    SearchQuery,
    SearchRank,
)
from django.contrib.postgres.indexes import GinIndex

from markdownx.models import MarkdownxField

from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.content.markdown import markdownify, extract_mentions


"""
Base abstract Activity class

We'll rename Content app to Activities: Content is easily confused with
contenttypes django contrib app.
"""


class Activity(TimeStampedModel):

    # all activities belong to a single community (at this point)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    # all activities are created by someone (this will become "owner" later)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    search_vector = SearchVectorField(null=True)

    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_vector"])]

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    def make_search_updater(self) -> Callable:
        def on_commit():
            search_vectors = [
                SearchVector(models.Value(text), weight=weight)
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_vector=reduce(operator.add, search_vectors)
            )

        return on_commit


# https://simonwillison.net/2018/Mar/25/combined-recent-additions/
"""
Example:
"""


def activity_stream(limit: int, **kwargs) -> List:
    querysets = []
    for key, queryset in kwargs.items():
        querysets.append(
            queryset.annotate(
                activity_type=models.Value(
                    key, output_field=models.CharField()
                )
            ).values("pk", "activity_type", "created")
        )
    union_qs = querysets[0].union(*querysets[1:])
    # TBD: pagination required
    results = [
        {"activity_type", "created", "pk"}
        for row in union_qs.order_by("-created")[:limit]
    ]
    # bulk load each object type
    to_load = defaultdict(set)
    for result in results:
        to_load[result["activity_type"]].add(result["pk"])
    fetched = {}
    for key, pks in to_load.items():
        for item in kwargs[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # annotate results with object
    for result in results:
        result["object"] = fetched[(result["activity_type"], result["pk"])]
    return results


"""
Example:

page = paginated_activity_stream(
    {
        "post":
        Post.objects.for_community(community=self.request.community),
        "photo":
        Photo.objects.for_community(community=self.request.community),
        "event":
        Event.objects.for_community(community=self.request.community),
    },
    **self.get_pagination_kwargs(),
)

{% for activity in activities %}

{% if activity.activity_type == 'post' %}
{% include "posts/includes/post.html" post=activity.object %}

{% elif activity.activity_type == 'photo' %}
{% include "photos/includes/photo.html" photo=activity.object %}

{% elif activity.activity_type == 'event' %}
{% include "events/includes/events.html" event=activity.object %}

{% empty %}
....
{% endfor %}


Search:

page = paginated_activity_search(
    self.search_query,
    self.get_querysets(),
    **self.get_pagination_kwargs(),
)

"""


def paginated_activity_search(
    search_term: str,
    queryset_dict: Dict[str, models.QuerySet],
    page_number: int,
    **paginator_kwargs,
) -> Page:

    query = SearchQuery(search_term)
    rank = SearchRank(models.F("search_vector"), query)

    queryset_dicts = {
        key: qs.annotate(rank=rank).filter(search_vector=query)
        for key, qs in queryset_dict.items()
    }
    return paginated_activity_stream(
        queryset_dicts, page_number, order_by="rank", **paginator_kwargs
    )


def paginated_activity_stream(
    queryset_dict: Dict[str, models.QuerySet],
    page_number: int,
    order_by: str = "created",
    **paginator_kwargs,
) -> Page:
    querysets = [
        queryset.annotate(
            activity_type=models.Value(key, output_field=models.CharField())
        ).values("pk", "activity_type", order_by)
        for key, queryset in queryset_dict.items()
    ]
    union_qs = querysets[0].union(*querysets[1:]).order_by(f"-{order_by}")
    page = Paginator(union_qs, **paginator_kwargs).get_page(page_number)
    # bulk load each object type
    to_load = defaultdict(set)
    for result in page:
        to_load[result["activity_type"]].add(result["pk"])
    fetched = {}
    for key, pks in to_load.items():
        for item in queryset_dict[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # annotate results with object
    for result in page:
        result["object"] = fetched[(result["activity_type"], result["pk"])]
    return page


# this will live in the "posts" app
class Post(Activity):

    title = models.CharField(blank=True, max_length=255)
    description = MarkdownxField(blank=True)
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.title or self.url

    def get_absolute_url(self) -> str:
        return reverse("posts:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())

    def markdown(self) -> str:
        return mark_safe(markdownify(self.description))

    def extract_mentions(self) -> Set[str]:
        """
        Return all @mentions in description
        """
        return extract_mentions(self.description)
