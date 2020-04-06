# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import BooleanField, Q, Value
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView, GenericModelView, ListView, UpdateView

from localhub.activities.models import get_activity_models
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.models import Comment
from localhub.comments.views import BaseCommentListView
from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.likes.models import Like
from localhub.private_messages.models import Message
from localhub.views import SearchMixin, SuccessMixin

from .forms import UserForm
from .utils import user_display


class BaseUserQuerySetMixin(CommunityRequiredMixin):
    def get_user_queryset(self):
        return get_user_model().objects.for_community(self.request.community)


class UserQuerySetMixin(BaseUserQuerySetMixin):
    def get_queryset(self):
        return self.get_user_queryset()


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self):
        return self.request.user


class SingleUserMixin(BaseUserQuerySetMixin):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.user_obj != self.request.user:
            self.user_obj.get_notifications().for_recipient(
                self.request.user
            ).mark_read()
        return response

    @cached_property
    def user_obj(self):
        return get_object_or_404(
            self.get_user_queryset(), username=self.kwargs["username"]
        )

    @cached_property
    def display_name(self):
        return user_display(self.user_obj)

    @cached_property
    def membership(self):
        return Membership.objects.filter(
            member=self.user_obj, community=self.request.community
        ).first()

    @cached_property
    def is_current_user(self):
        return self.user_obj == self.request.user

    @cached_property
    def is_blocked(self):
        return self.is_blocker or self.is_blocking

    @cached_property
    def is_following(self):
        return (
            not self.is_current_user
            and self.user_obj in self.request.user.following.all()
        )

    @cached_property
    def is_blocker(self):
        if self.is_current_user:
            return False
        return self.request.user.blockers.filter(pk=self.user_obj.id).exists()

    @cached_property
    def is_blocking(self):
        if self.is_current_user:
            return False
        return self.request.user.blocked.filter(pk=self.user_obj.id).exists()

    @cached_property
    def unread_messages(self):
        if self.is_current_user:
            return 0

        return (
            Message.objects.from_sender_to_recipient(self.user_obj, self.request.user)
            .unread()
            .count()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "user_obj": self.user_obj,
                "is_current_user": self.is_current_user,
                "is_blocked": self.is_blocked,
                "is_blocker": self.is_blocker,
                "is_blocking": self.is_blocking,
                "is_following": self.is_following,
                "display_name": self.display_name,
                "membership": self.membership,
                "unread_messages": self.unread_messages,
            }
        )
        return data


class BaseSingleUserView(UserQuerySetMixin, SuccessMixin, GenericModelView):
    lookup_field = "username"
    lookup_url_kwarg = "username"


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_role(self.request.community)
            .order_by("name", "username")
            .exclude(blocked=self.request.user)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["blocked_users"] = self.request.user.get_blocked_users()
        return data


class BaseFollowUserView(PermissionRequiredMixin, BaseSingleUserView):
    permission_required = "users.follow_user"
    template_name = "users/includes/follow.html"

    def success_response(self, is_following):
        return self.render_to_response(
            {"user_obj": self.object, "is_following": is_following}
        )


class UserFollowView(BaseFollowUserView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.request.user.following.add(self.object)
        self.request.user.notify_on_follow(self.object, self.request.community)

        return self.success_response(is_following=True)


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseFollowUserView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following.remove(self.object)
        return self.success_response(is_following=False)


user_unfollow_view = UserUnfollowView.as_view()


class UserBlockView(PermissionRequiredMixin, BaseSingleUserView):
    permission_required = "users.block_user"
    success_message = _("You are now blocking this user")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked.add(self.object)
        return self.success_response()


user_block_view = UserBlockView.as_view()


class UserUnblockView(BaseSingleUserView):
    success_message = _("You have stopped blocking this user")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked.remove(self.object)
        return self.success_response()


user_unblock_view = UserUnblockView.as_view()


class FollowingUserListView(BaseUserListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self):
        return (
            self.request.user.following.annotate(
                is_following=Value(True, output_field=BooleanField())
            )
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_num_unread_messages(self.request.user, self.request.community)
            .order_by("name", "username")
        )


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(BaseUserListView):
    template_name = "users/follower_user_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(following=self.request.user)
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(BaseUserListView):
    template_name = "users/blocked_user_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(blockers=self.request.user)
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
        )


blocked_user_list_view = BlockedUserListView.as_view()


class MemberListView(SearchMixin, BaseUserListView):
    """
    Shows all members of community
    """

    template_name = "users/member_list.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .exclude(blocked=self.request.user)
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

    def get_queryset(self):
        qs = super().get_queryset().exclude(blocked=self.request.user)
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            return qs.filter(
                Q(
                    Q(username__istartswith=search_term)
                    | Q(name__istartswith=search_term)
                )
            )[: settings.LOCALHUB_DEFAULT_PAGE_SIZE]
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()


class UserStreamView(SingleUserMixin, BaseActivityStreamView):

    active_tab = "posts"
    template_name = "users/activities.html"

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
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*get_activity_models())
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_stream_view = UserStreamView.as_view()


class UserCommentListView(SingleUserMixin, BaseCommentListView):
    active_tab = "comments"
    template_name = "users/comments.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.user_obj).order_by("-created")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_comment_list_view = UserCommentListView.as_view()


class UserMessageListView(SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/messages.html"
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE

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


user_message_list_view = UserMessageListView.as_view()


class UserUpdateView(
    CurrentUserMixin, PermissionRequiredMixin, SuccessMixin, UpdateView,
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
        return self.success_response()


user_update_view = UserUpdateView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class DismissNoticeView(CurrentUserMixin, View):
    def post(self, request, notice):
        self.request.user.dismiss_notice(notice)
        return HttpResponse()


dismiss_notice_view = DismissNoticeView.as_view()


class SwitchThemeView(View):
    def post(self, request, theme):
        if theme not in settings.LOCALHUB_INSTALLED_THEMES:
            raise Http404()

        response = HttpResponse()
        response.set_cookie(
            "theme",
            theme,
            expires=datetime.datetime.now() + datetime.timedelta(days=365),
            domain=settings.SESSION_COOKIE_DOMAIN,
            httponly=True,
        )
        return response


switch_theme_view = SwitchThemeView.as_view()
