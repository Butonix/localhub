# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext as _

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import BaseCommentListView
from localhub.views import PageTitleMixin


class BookmarksPageTitleMixin(PageTitleMixin):
    def get_page_title_segments(self):
        return [_("Bookmarks")]


class BookmarksStreamView(BookmarksPageTitleMixin, BaseActivityStreamView):
    # tbd: make searchable...
    template_name = "bookmarks/activities.html"

    def get_page_title_segments(self):
        return super().get_page_title_segments() + [_("Activities")]

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(
            model.objects.with_has_bookmarked(self.request.user)
        )

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(has_bookmarked=True)


bookmarks_stream_view = BookmarksStreamView.as_view()


class BookmarksCommentListView(BookmarksPageTitleMixin, BaseCommentListView):
    template_name = "bookmarks/comments.html"

    def get_page_title_segments(self):
        return super().get_page_title_segments() + [_("Comments")]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .filter(has_bookmarked=True)
            .order_by("-created")
        )


bookmarks_comment_list_view = BookmarksCommentListView.as_view()