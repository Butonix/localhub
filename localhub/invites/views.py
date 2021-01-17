# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import http

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, DetailView, ListView

# Third Party Libraries
from turbo_response import TemplateFormResponse, redirect_303

# Localhub
from localhub.common.decorators import add_messages_to_response_header
from localhub.common.forms import process_form
from localhub.common.mixins import SearchMixin
from localhub.communities.decorators import community_admin_required
from localhub.communities.mixins import CommunityAdminRequiredMixin

# Local
from .emails import send_invitation_email
from .forms import InviteForm
from .mixins import InviteQuerySetMixin, InviteRecipientQuerySetMixin
from .models import Invite


@community_admin_required
@login_required
@add_messages_to_response_header
@require_POST
def invite_resend_view(request, pk):
    invite = get_invite_or_404(request, pk)
    invite.sent = timezone.now()
    invite.save()

    send_invitation_email(invite)
    messages.success(
        request,
        _("Your invitation has been re-sent to %(email)s") % {"email": invite.email},
    )

    return HttpResponse(status=http.HTTPStatus.NO_CONTENT)


@login_required
@require_POST
def invite_accept_view(request, pk):
    """
    Handles an invite accept action.

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    invite = get_recipient_invite_or_404(request, pk)
    invite.accept(request.user)
    request.user.notify_on_join(invite.community)

    messages.success(
        request,
        _("You are now a member of %(community)s")
        % {"community": invite.community.name},
    )

    return redirect(
        settings.HOME_PAGE_URL
        if invite.is_accepted() and request.community == invite.community
        else "invites:received_list"
    )


@login_required
@require_POST
def invite_reject_view(request, pk):
    invite = get_recipient_invite_or_404(request, pk)
    invite.reject()

    return redirect(
        "invites:received_list"
        if Invite.objects.pending().for_user(request.user).exists()
        else settings.HOME_PAGE_URL
    )


@community_admin_required
@login_required
def invite_create_view(request):

    with process_form(request, InviteForm, community=request.community) as (
        form,
        success,
    ):
        if success:

            invite = form.save(commit=False)
            invite.sender = request.user
            invite.community = request.community
            invite.sent = timezone.now()
            invite.save()

            # send email to recipient
            send_invitation_email(invite)

            messages.success(
                request,
                _("Your invitation has been sent to %(email)s")
                % {"email": invite.email},
            )
            return redirect_303("invites:list")

        return TemplateFormResponse(request, form, "invites/invite_form.html")


class InviteDeleteView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, DeleteView,
):
    success_url = reverse_lazy("invites:list")
    success_message = _("You have deleted this invite")
    model = Invite

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


invite_delete_view = InviteDeleteView.as_view()


class InviteDetailView(InviteRecipientQuerySetMixin, DetailView):
    ...


invite_detail_view = InviteDetailView.as_view()


class InviteListView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SearchMixin, ListView
):
    """
    TBD: list of received pending community invitations
    + counter template tag
    """

    model = Invite
    paginate_by = settings.LONG_PAGE_SIZE

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.filter(email__icontains=self.search_query)

        if self.status:
            qs = qs.filter(status=self.status)

        return qs.order_by("-created")

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in Invite.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(Invite.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(Invite.Status.choices),
            }
        )
        return data


invite_list_view = InviteListView.as_view()


class ReceivedInviteListView(InviteRecipientQuerySetMixin, ListView):
    """
    List of pending invites sent to this user from different communities.
    """

    template_name = "invites/received_invite_list.html"
    paginate_by = settings.LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("-created")


received_invite_list_view = ReceivedInviteListView.as_view()


def get_invite_or_404(request, pk):
    return get_object_or_404(get_invite_queryset(request), pk=pk)


def get_recipient_invite_or_404(request, pk):
    return get_object_or_404(get_recipient_invite_queryset(request), pk=pk)


def get_invite_queryset(request):
    return Invite.objects.for_community(request.community).select_related("community")


def get_recipient_invite_queryset(request):
    return Invite.objects.pending().for_user(request.user).select_related("community")
