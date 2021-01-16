# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import resolve
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import HttpResponseSeeOther, TurboFrame, TurboStream
from turbo_response.views import TurboUpdateView

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.models import Comment
from localhub.comments.views import BaseCommentListView
from localhub.common.mixins import SearchMixin
from localhub.common.views import ActionView
from localhub.communities.decorators import community_required
from localhub.communities.rules import is_member
from localhub.likes.models import Like
from localhub.private_messages.models import Message

# Local
from .forms import UserForm
from .mixins import (
    CurrentUserMixin,
    MemberQuerySetMixin,
    SingleUserMixin,
    UserQuerySetMixin,
)
from .utils import has_perm_or_403


class BaseUserActivityStreamView(SingleUserMixin, BaseActivityStreamView):
    ...


class BaseUserCommentListView(SingleUserMixin, BaseCommentListView):
    ...


class UserPreviewView(MemberQuerySetMixin, UserQuerySetMixin, DetailView):
    template_name = "users/preview.html"
    context_object_name = "user_obj"
    slug_field = "username"
    slug_url_kwarg = "username"

    def render_to_response(self, context, **response_kwargs):
        return (
            TurboFrame(f"user-preview-{self.object.id}")
            .template(self.template_name, context)
            .response(self.request)
        )

    def get_object_url(self):
        """Allow a different object url e.g. to message or comment tabs."""
        url = self.request.GET.get("object_url")
        if url and url_has_allowed_host_and_scheme(url, settings.ALLOWED_HOSTS):
            try:
                resolve(url)
                return url
            except Http404:
                pass
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "object_url": self.get_object_url(),
        }


user_preview_view = UserPreviewView.as_view()


class UserStreamView(BaseUserActivityStreamView):

    template_name = "users/detail/activities.html"

    def get_ordering(self):
        if self.is_current_user:
            return ("-created", "-published")
        return "-published"

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .exclude_blocked_tags(self.request.user)
            .filter(owner=self.user_obj)
        )
        if self.is_current_user:
            return qs.published_or_owner(self.request.user)
        return qs.published()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "num_likes": (
                    Like.objects.for_models(*get_activity_models())
                    .filter(recipient=self.user_obj, community=self.request.community)
                    .count()
                )
            },
        }


user_stream_view = UserStreamView.as_view()


class UserCommentListView(BaseUserCommentListView):
    template_name = "users/detail/comments.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.user_obj).order_by("-created")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "num_likes": (
                    Like.objects.for_models(Comment)
                    .filter(recipient=self.user_obj, community=self.request.community)
                    .count()
                )
            },
        }


user_comment_list_view = UserCommentListView.as_view()


class UserMessageListView(LoginRequiredMixin, SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/detail/messages.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self):
        if self.is_blocked:
            return Message.objects.none()
        qs = (
            Message.objects.for_community(self.request.community)
            .common_select_related()
            .order_by("-created")
            .distinct()
        )

        if self.is_current_user:
            qs = qs.for_sender_or_recipient(self.request.user)
        else:
            qs = qs.between(self.request.user, self.user_obj)
        return qs

    def get_num_messages_sent(self):
        return self.get_queryset().filter(sender=self.request.user).count()

    def get_num_messages_received(self):
        return self.get_queryset().filter(recipient=self.request.user).count()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "sent_messages": self.get_num_messages_sent(),
                "received_messages": self.get_num_messages_received(),
            },
        }


user_message_list_view = UserMessageListView.as_view()


class UserActivityLikesView(BaseUserActivityStreamView):
    """Liked activities published by this user."""

    template_name = "users/likes/activities.html"
    ordering = ("-num_likes", "-published")

    exclude_blocking_users = True

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .with_num_likes()
            .published()
            .filter(owner=self.user_obj, num_likes__gt=0)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*get_activity_models())
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_activity_likes_view = UserActivityLikesView.as_view()


class UserCommentLikesView(BaseUserCommentListView):
    """Liked comments submitted by this user."""

    template_name = "users/likes/comments.html"

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(owner=self.user_obj, num_likes__gt=0)
            .order_by("-num_likes", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_comment_likes_view = UserCommentLikesView.as_view()


class UserActivityMentionsView(BaseUserActivityStreamView):
    """Activities where the user has an @mention (only
    published activities were user is not the owner)
    """

    template_name = "users/mentions/activities.html"

    exclude_blocking_users = True

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
        )


user_activity_mentions_view = UserActivityMentionsView.as_view()


class UserCommentMentionsView(BaseUserCommentListView):

    template_name = "users/mentions/comments.html"

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
            .order_by("-created")
        )


user_comment_mentions_view = UserCommentMentionsView.as_view()


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("name", "username")


class BaseMemberListView(MemberQuerySetMixin, BaseUserListView):

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )


class MemberListView(SearchMixin, BaseMemberListView):
    """
    Shows all members of community
    """

    template_name = "users/list/members.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


class FollowingUserListView(LoginRequiredMixin, BaseMemberListView):
    template_name = "users/list/following.html"

    def get_queryset(self):
        return super().get_queryset().filter(followers=self.request.user)


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(LoginRequiredMixin, BaseMemberListView):
    template_name = "users/list/followers.html"

    def get_queryset(self):
        return super().get_queryset().filter(following=self.request.user)


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(LoginRequiredMixin, MemberQuerySetMixin, BaseUserListView):
    template_name = "users/list/blocked.html"

    def get_queryset(self):
        return super().get_queryset().filter(blockers=self.request.user)


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/list/autocomplete.html"

    exclude_blocking_users = True

    def get_queryset(self):
        qs = super().get_queryset()
        # exclude current user by default
        if self.request.user.is_authenticated:
            qs = qs.exclude(pk=self.request.user.pk)
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            return qs.filter(
                Q(Q(username__icontains=search_term) | Q(name__icontains=search_term))
            )[: settings.DEFAULT_PAGE_SIZE]
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()


class UserUpdateView(
    SuccessMessageMixin, CurrentUserMixin, PermissionRequiredMixin, TurboUpdateView,
):
    permission_required = "users.change_user"
    success_message = _("Your details have been updated")
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        self.object = form.save()
        self.object.notify_on_update()
        return HttpResponseSeeOther(self.get_success_url())

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "is_community": self.request.community.active
                and is_member(self.request.user, self.request.community)
            },
        }


user_update_view = UserUpdateView.as_view()


class BaseUserActionView(PermissionRequiredMixin, UserQuerySetMixin, ActionView):
    slug_field = "username"
    slug_url_kwarg = "username"


class BaseFollowUserView(BaseUserActionView,):
    permission_required = "users.follow_user"
    exclude_blocking_users = True

    def render_to_response(self, is_following):
        is_detail = self.request.POST.get("is_detail", False)
        return (
            TurboFrame(f"user-{self.object.id}-follow")
            .template(
                "users/includes/follow.html",
                {
                    "object": self.object,
                    "is_following": is_following,
                    "is_detail": is_detail,
                },
            )
            .response(self.request)
        )


class UserFollowView(BaseFollowUserView):
    success_message = _("You are now following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.add(self.object)
        self.request.user.notify_on_follow(self.object, self.request.community)
        return self.render_to_response(is_following=True)


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseFollowUserView):
    success_message = _("You are no longer following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.remove(self.object)
        return self.render_to_response(is_following=False)


user_unfollow_view = UserUnfollowView.as_view()


@community_required
@login_required
@require_POST
def user_block_view(request, username, remove=False):
    user = get_user_or_404(
        request,
        username,
        queryset=get_user_queryset(request, exclude=None),
        permission="users.block_user",
    )

    if remove:
        request.user.blocked.remove(user)
        messages.info(request, _("You are no longer blocking this user"))
    else:
        request.user.block_user(user)
        messages.success(request, _("You are now blocking this user"))

    return redirect(user)


@login_required
def user_delete_view(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect(settings.HOME_PAGE_URL)
    return TemplateResponse(request, "users/user_confirm_delete.html")


@login_required
@require_POST
def dismiss_notice_view(request, notice):
    request.user.dismiss_notice(notice)
    return TurboStream(f"notice-{notice}").remove.response()


@require_POST
def accept_cookies(request):
    response = TurboStream("accept-cookies").remove.response()
    response.set_cookie(
        "accept-cookies",
        value="true",
        expires=timezone.now() + datetime.timedelta(days=30),
        samesite="Lax",
    )
    return response


def get_user_or_404(request, username, *, queryset=None, permission=None):
    user = get_object_or_404(
        queryset or get_user_queryset(request), username__iexact=username
    )
    if permission:
        has_perm_or_403(request.user, permission, user)
    return user


def get_user_queryset(request, exclude="blocking"):
    qs = get_user_model().objects.for_community(request.community)

    if exclude == "blocking":
        qs = qs.exclude_blocking(request.user)

    elif exclude == "blocked":
        qs = qs.exclude_blocked(request.user)

    elif exclude == "blockers":
        qs = qs.exclude_blockers(request.user)

    return qs
