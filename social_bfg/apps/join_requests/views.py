# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin

# Social-BFG
from social_bfg.apps.communities.models import Membership
from social_bfg.apps.communities.views import (
    CommunityAdminRequiredMixin,
    CommunityRequiredMixin,
)
from social_bfg.views import (
    SearchMixin,
    SuccessActionView,
    SuccessCreateView,
    SuccessDeleteView,
)

# Local
from .emails import send_acceptance_email, send_join_request_email, send_rejection_email
from .forms import JoinRequestForm
from .models import JoinRequest


class JoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return JoinRequest.objects.for_community(self.request.community)


class JoinRequestAdminMixin(PermissionRequiredMixin):
    permission_required = "communities.manage_community"

    def get_permission_object(self):
        return self.request.community


class BaseJoinRequestActionView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, SuccessActionView
):
    success_url = reverse_lazy("join_requests:list")


class JoinRequestAcceptView(BaseJoinRequestActionView):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                status__in=(JoinRequest.Status.PENDING, JoinRequest.Status.REJECTED)
            )
        )

    def get_success_message(self):
        return _("Join request for %(sender)s has been accepted") % {
            "sender": self.object.sender.get_display_name()
        }

    def post(self, request, *args, **kwargs):
        if Membership.objects.filter(
            member=self.object.sender, community=self.object.community
        ).exists():
            messages.error(request, _("User already belongs to this community"))
            return HttpResponseRedirect(reverse("join_requests:list"))

        self.object.accept()

        Membership.objects.create(
            member=self.object.sender, community=self.object.community
        )

        send_acceptance_email(self.object)

        self.object.sender.notify_on_join(self.object.community)

        return self.success_response()


join_request_accept_view = JoinRequestAcceptView.as_view()


class JoinRequestRejectView(BaseJoinRequestActionView):
    def get_queryset(self):
        return super().get_queryset().pending()

    def get_success_message(self):
        return (
            _("Join request for %(sender)s has been rejected")
            % {"sender": self.object.sender.get_display_name()},
        )

    def post(self, request, *args, **kwargs):
        self.object.reject()
        send_rejection_email(self.object)
        return self.success_response()


join_request_reject_view = JoinRequestRejectView.as_view()
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class JoinRequestCreateView(
    PermissionRequiredMixin, CommunityRequiredMixin, SuccessCreateView,
):
    model = JoinRequest
    form_class = JoinRequestForm
    template_name = "join_requests/joinrequest_form.html"
    allow_non_members = True
    permission_required = "join_requests.create"
    success_message = _("Your request has been sent to the community admins")

    def get_permission_object(self):
        return self.request.community

    def get_form_kwargs(self, *args, **kwargs):
        return {
            **super().get_form_kwargs(),
            **{"user": self.request.user, "community": self.request.community},
        }

    def form_valid(self, form):
        self.object = form.save()
        send_join_request_email(self.object)
        return self.success_response()

    def get_success_url(self):
        return reverse("community_welcome")


join_request_create_view = JoinRequestCreateView.as_view()
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class JoinRequestDeleteView(PermissionRequiredMixin, SuccessDeleteView):
    model = JoinRequest
    permission_required = "join_requests.delete"

    def get_queryset(self):
        return super().get_queryset().select_related("community", "sender")

    @cached_property
    def is_sender(self):
        return self.object.sender == self.request.user

    def get_success_url(self):
        if self.is_sender:
            if JoinRequest.objects.for_sender(self.request.user).exists():
                return reverse("join_requests:sent_list")
            return settings.SOCIAL_BFG_HOME_PAGE_URL
        return reverse("join_requests:list")

    def get_success_message(self):
        if self.is_sender:
            return _("Your join request for %(community)s has been deleted") % {
                "community": self.object.community.name
            }
        return _("Join request for %(sender)s has been deleted") % {
            "sender": self.object.sender.get_display_name()
        }


join_request_delete_view = JoinRequestDeleteView.as_view()
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class JoinRequestDetailView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, DetailView
):
    model = JoinRequest


join_request_detail_view = JoinRequestDetailView.as_view()
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class JoinRequestListView(
    JoinRequestQuerySetMixin, JoinRequestAdminMixin, SearchMixin, ListView
):
    paginate_by = settings.SOCIAL_BFG_LONG_PAGE_SIZE
    model = JoinRequest

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in JoinRequest.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(JoinRequest.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_queryset(self):
        qs = super().get_queryset().select_related("community", "sender")
        if self.search_query:
            qs = qs.search(self.search_query)

        if self.status:
            qs = qs.filter(status=self.status).order_by("-created")
        else:
            qs = qs.annotate(
                priority=Case(
                    When(status=JoinRequest.Status.PENDING, then=Value(1)),
                    default_value=0,
                    output_field=IntegerField(),
                )
            ).order_by("priority", "-created")
        return qs

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(JoinRequest.Status.choices),
            },
        }


join_request_list_view = JoinRequestListView.as_view()


class SentJoinRequestListView(LoginRequiredMixin, ListView):
    """
    List of pending join requests sent by this user
    """

    model = JoinRequest
    paginate_by = settings.SOCIAL_BFG_LONG_PAGE_SIZE
    template_name = "join_requests/sent_joinrequest_list.html"

    def get_queryset(self):
        return (
            JoinRequest.objects.pending()
            .for_sender(self.request.user)
            .select_related("community")
            .order_by("-created")
        )


sent_join_request_list_view = SentJoinRequestListView.as_view()
