# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from . import generic


def create_activity_urls(
    model,
    form_class=None,
    list_view_class=generic.ActivityListView,
    create_view_class=generic.ActivityCreateView,
    update_view_class=generic.ActivityUpdateView,
    detail_view_class=generic.ActivityDetailView,
    delete_view_class=generic.ActivityDeleteView,
    dislike_view_class=generic.ActivityDislikeView,
    flag_view_class=generic.ActivityFlagView,
    like_view_class=generic.ActivityLikeView,
    reshare_view_class=generic.ActivityReshareView,
    create_comment_view_class=generic.ActivityCommentCreateView,
):
    """
    Generates default URL patterns for activity subclasses.

    Simple usage (in a urls.py)

    urlpatterns = create_activity_urls(Post)
    # add more urlpatterns...
    """
    return [
        path("", list_view_class.as_view(model=model), name="list"),
        path(
            "~create",
            create_view_class.as_view(model=model, form_class=form_class),
            name="create",
        ),
        path(
            "<int:pk>/~comment/",
            create_comment_view_class.as_view(model=model),
            name="comment",
        ),
        path(
            "<int:pk>/~delete/",
            delete_view_class.as_view(model=model),
            name="delete",
        ),
        path(
            "<int:pk>/~dislike/",
            dislike_view_class.as_view(model=model),
            name="dislike",
        ),
        path(
            "<int:pk>/~flag/",
            flag_view_class.as_view(model=model),
            name="flag",
        ),
        path(
            "<int:pk>/~like/",
            like_view_class.as_view(model=model),
            name="like",
        ),
        path(
            "<int:pk>/~reshare/",
            reshare_view_class.as_view(model=model),
            name="reshare",
        ),
        path(
            "<int:pk>/~update/",
            update_view_class.as_view(model=model, form_class=form_class),
            name="update",
        ),
        path(
            "<int:pk>/<slug:slug>/",
            detail_view_class.as_view(model=model),
            name="detail",
        ),
        path(
            "<int:pk>/",
            detail_view_class.as_view(model=model),
            name="detail_no_slug",
        ),
    ]
