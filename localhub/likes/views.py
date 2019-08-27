# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from localhub.activities.views.streams import BaseStreamView
from localhub.comments.views import CommentListView


class LikedStreamView(LoginRequiredMixin, BaseStreamView):
    template_name = "likes/activities.html"

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(
            model.objects.with_has_liked(self.request.user)
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(has_liked=True)


liked_stream_view = LikedStreamView.as_view()


class LikedCommentListView(LoginRequiredMixin, CommentListView):
    template_name = "likes/comments.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
            .filter(has_liked=True)
            .order_by("-created")
        )


liked_comment_list_view = LikedCommentListView.as_view()
