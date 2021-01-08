# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import HttpResponseSeeOther, TurboFrame, TurboStream
from turbo_response.views import TurboCreateView, TurboFormView, TurboUpdateView

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.comments.forms import CommentForm
from localhub.common.mixins import ParentObjectMixin, SearchMixin
from localhub.common.pagination import PresetCountPaginator
from localhub.common.template.defaultfilters import resolve_url
from localhub.communities.mixins import CommunityPermissionRequiredMixin
from localhub.flags.views import BaseFlagCreateView
from localhub.likes.models import Like

# Local
from ..forms import ActivityTagsForm
from ..mixins import ActivityQuerySetMixin, ActivityTemplateMixin
from ..utils import get_activity_models


class ActivityCreateView(
    SuccessMessageMixin,
    CommunityPermissionRequiredMixin,
    ActivityTemplateMixin,
    TurboCreateView,
):
    permission_required = "activities.create_activity"

    is_private = False
    is_new = True

    def get_success_message(self):
        return super().get_success_message(
            _("Your %(model)s has been published")
            if self.object.published
            else _("Your %(model)s has been saved to your Private Stash")
        )

    def get_submit_actions(self):
        view_name = "create_private" if self.is_private else "create"
        return [
            (
                resolve_url(model, view_name),
                _("Submit %(model)s")
                % {"model": model._meta.verbose_name.capitalize()},
            )
            for model in get_activity_models()
            if model != self.model
        ]

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["submit_actions"] = self.get_submit_actions()
        return data

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):

        publish = self.is_private is False and "save_private" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            self.object.notify_on_publish()

        return HttpResponseSeeOther(self.get_success_url())


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, BaseFlagCreateView
):
    permission_required = "activities.flag_activity"
    success_message = _("This %(model)s has been flagged to the moderators")

    def get_parent_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.parent


activity_flag_view = ActivityFlagView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ParentObjectMixin, TurboFormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"
    success_message = _("Your comment has been posted")

    parent_context_object_name = "content_object"

    def get_permission_object(self):
        return self.parent

    def get_parent_queryset(self):
        return self.get_queryset()

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.parent
        self.object.community = self.request.community
        self.object.owner = self.request.user
        self.object.save()

        self.object.notify_on_create()

        messages.success(
            self.request, self.success_message,
        )

        return HttpResponseSeeOther(self.get_success_url())


class ActivityUpdateView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    TurboUpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been updated")

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.update_reshares()

        if self.object.published:
            self.object.notify_on_update()

        messages.success(
            self.request,
            self.success_message % {"model": self.object._meta.verbose_name},
        )

        return HttpResponseSeeOther(self.get_success_url())


class ActivityUpdateTagsView(ActivityUpdateView):
    """
    Allows a moderator to update the tags on a view, e.g
    to add a "content sensitive" tag.
    """

    form_class = ActivityTagsForm
    permission_required = "activities.change_activity_tags"
    success_message = _("Tags have been updated")

    def get_queryset(self):
        return super().get_queryset().published()


class BaseActivityListView(ActivityQuerySetMixin, ActivityTemplateMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE


class ActivityListView(SearchMixin, BaseActivityListView):
    ordering = ("-created", "-published")

    def get_ordering(self):
        if isinstance(self.ordering, str):
            ordering = [self.ordering]
        else:
            ordering = list(self.ordering)

        if self.search_query:
            ordering = ["-rank"] + ordering

        return ordering

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked(self.request.user)
        )

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs.order_by(*self.get_ordering())


class ActivityDetailView(ActivityQuerySetMixin, ActivityTemplateMixin, DetailView):
    paginator_class = PresetCountPaginator
    paginate_by = settings.DEFAULT_PAGE_SIZE
    page_kwarg = "page"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.object.get_notifications().for_recipient(
                self.request.user
            ).unread().update(is_read=True)
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()

        data["comments"] = self.get_comments_page(self.get_comments())
        if self.request.user.has_perm("activities.create_comment", self.object):
            data["comment_form"] = CommentForm()

        data["reshares"] = self.get_reshares()
        return data

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("editor")
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
        )

    def get_flags(self):
        return (
            self.object.get_flags()
            .select_related("user")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    def get_reshares(self):
        return (
            self.object.reshares.for_community(self.request.community)
            .exclude_blocked_users(self.request.user)
            .select_related("owner")
            .order_by("-created")
        )

    def get_comments(self):
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.user, self.request.community)
            .for_community(self.request.community)
            .exclude_deleted()
            .with_common_related()
            .order_by("created")
        )

    def get_comments_page(self, comments):
        return self.paginator_class(
            object_list=comments,
            count=self.object.num_comments or 0,
            per_page=self.paginate_by,
            allow_empty_first_page=True,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))


class BaseActivityActionView(
    ActivityQuerySetMixin, PermissionRequiredMixin, SingleObjectMixin, View
):
    def get_success_url(self):
        return self.object.get_absolute_url()

    @cached_property
    def object(self):
        return self.get_object()

    def get_response(self):
        return HttpResponseRedirect(self.get_success_url())


class ActivityReshareView(BaseActivityActionView):
    permission_required = "activities.reshare_activity"
    success_message = _("You have reshared this %(model)s")

    def get_queryset(self):
        """
        Make sure user has only reshared once.
        """
        return super().get_queryset().unreshared(self.request.user)

    def get_success_url(self):
        return self.reshare.get_absolute_url()

    def post(self, request, *args, **kwargs):
        self.reshare = self.object.reshare(self.request.user)

        self.reshare.notify_on_publish()

        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )

        return self.get_response()


class ActivityPublishView(BaseActivityActionView):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been published")

    def get_queryset(self):
        return super().get_queryset().filter(published__isnull=True)

    def post(self, request, *args, **kwargs):
        self.object.published = timezone.now()
        self.object.save(update_fields=["published"])
        self.object.notify_on_publish()
        return self.get_response()


activity_publish_view = ActivityPublishView.as_view()


class ActivityPinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been pinned to the top of the activity stream"
    )

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        for model in get_activity_models():
            model.objects.for_community(community=request.community).update(
                is_pinned=False
            )

        self.object.is_pinned = True
        self.object.save()

        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )
        return self.get_response()


class ActivityUnpinView(BaseActivityActionView):
    permission_required = "activities.pin_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _(
        "The %(model)s has been unpinned from the top of the activity stream"
    )

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        self.object.is_pinned = False
        self.object.save()
        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )
        return self.get_response()


class BaseActivityBookmarkView(BaseActivityActionView):
    permission_required = "activities.bookmark_activity"

    def get_response(self, has_bookmarked):
        return (
            TurboFrame(self.object.get_dom_id() + "-bookmark")
            .template(
                "activities/includes/bookmark.html",
                {"object": self.object, "has_bookmarked": has_bookmarked},
            )
            .response(self.request)
        )


class ActivityBookmarkView(BaseActivityBookmarkView):
    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            # dupe, ignore
            pass
        return self.get_response(has_bookmarked=True)


class ActivityRemoveBookmarkView(BaseActivityBookmarkView):
    def post(self, request, *args, **kwargs):
        self.object.get_bookmarks().filter(user=request.user).delete()
        return self.get_response(has_bookmarked=False)


class BaseActivityLikeView(BaseActivityActionView):
    permission_required = "activities.like_activity"

    def get_response(self, has_liked):
        return (
            TurboFrame(self.object.get_dom_id() + "-like")
            .template(
                "activities/includes/like.html",
                {"object": self.object, "has_liked": has_liked},
            )
            .response(self.request)
        )


class ActivityLikeView(BaseActivityLikeView):
    def post(self, request, *args, **kwargs):
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            ).notify()

        except IntegrityError:
            # dupe, ignore
            pass
        return self.get_response(has_liked=True)


class ActivityDislikeView(BaseActivityLikeView):
    def post(self, request, *args, **kwargs):
        self.object.get_likes().filter(user=request.user).delete()
        return self.get_response(has_liked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityDeleteView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ActivityTemplateMixin, DeleteView,
):
    permission_required = "activities.delete_activity"
    success_message = _("You have deleted this %(model)s")

    def get_success_url(self):
        if self.object.deleted or self.object.published:
            return settings.HOME_PAGE_URL
        return reverse("activities:private")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        target = request.POST.get("target", None)
        if target:
            return TurboStream(target).remove.response()

        messages.success(
            request, self.success_message % {"model": self.object._meta.verbose_name}
        )

        return HttpResponseRedirect(self.get_success_url())
