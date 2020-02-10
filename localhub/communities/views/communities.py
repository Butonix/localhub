# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DetailView, ListView, TemplateView, UpdateView

from localhub.activities.utils import get_combined_activity_queryset
from localhub.join_requests.models import JoinRequest
from localhub.views import SearchMixin

from ..models import Community, Membership
from ..rules import is_member
from .base import CommunityRequiredMixin


class CommunityDetailView(CommunityRequiredMixin, DetailView):
    model = Community

    def get_object(self):
        return self.request.community


community_detail_view = CommunityDetailView.as_view()


class CommunityTermsView(CommunityDetailView):
    template_name = "communities/terms.html"


community_terms_view = CommunityTermsView.as_view()


class CommunityNotFoundView(TemplateView):
    """
    This is shown if no community exists for this domain.
    """

    template_name = "communities/not_found.html"


community_not_found_view = CommunityNotFoundView.as_view()


class CommunityWelcomeView(CommunityRequiredMixin, TemplateView):
    """
    This is shown if the user is not a member (or is not authenticated).

    If user is already a member, redirects to home page.
    """

    template_name = "communities/welcome.html"
    allow_non_members = True

    def get(self, request, *args, **kwargs):
        if is_member(request.user, request.community):
            return HttpResponseRedirect(settings.HOME_PAGE_URL)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if not is_member(self.request.user, self.request.community):
            data["join_request"] = JoinRequest.objects.filter(
                sender=self.request.user, community=self.request.community
            ).first()
        return data


community_welcome_view = CommunityWelcomeView.as_view()


class CommunityUpdateView(CommunityRequiredMixin, PermissionRequiredMixin, UpdateView):
    fields = (
        "name",
        "logo",
        "tagline",
        "intro",
        "description",
        "terms",
        "google_tracking_id",
        "content_warning_tags",
        "listed",
        "allow_join_requests",
        "blacklisted_email_domains",
        "blacklisted_email_addresses",
    )

    permission_required = "communities.manage_community"
    success_message = _("Community settings have been updated")
    model = Community

    def get_object(self):
        return self.request.community

    def get_success_url(self):
        return self.request.path

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form: ModelForm):
        community = form.save(commit=False)
        community.admin = self.request.user
        community.save()
        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


community_update_view = CommunityUpdateView.as_view()


class CommunityListView(LoginRequiredMixin, SearchMixin, ListView):
    """
    Returns all public communities, or communities the
    current user belongs to.
    """

    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_template_names(self):
        if self.request.community and is_member(
            self.request.user, self.request.community
        ):
            return ["communities/member_community_list.html"]
        return ["communities/non_member_community_list.html"]

    def get_queryset(self):
        qs = Community.objects.listed(self.request.user).order_by("name")
        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)
        return qs

    def get_member_communities(self):
        return Community.objects.filter(
            membership__member=self.request.user, membership__active=True
        ).exclude(pk=self.request.community.id)

    def get_available_users(self):
        return (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=self.request.user.blocked.all())
        )

    def get_drafts_count(self):
        communities = self.get_member_communities()

        drafts = get_combined_activity_queryset(
            lambda model: model.objects.filter(community__in=communities)
            .drafts(self.request.user)
            .only("pk", "community")
        )

        return {
            community.id: len(
                [draft for draft in drafts if draft.community_id == community.id]
            )
            for community in communities
        }

    def get_notifications_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_notifications=Count(
                    "notification",
                    filter=Q(
                        notification__recipient=self.request.user,
                        notification__is_read=False,
                        notification__actor__pk__in=self.get_available_users(),
                        notification__actor__membership__active=True,
                        notification__actor__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_notifications")
        )

    def get_flags_count(self):
        return dict(
            self.get_member_communities()
            .filter(
                membership__role__in=(
                    Membership.ROLES.admin,
                    Membership.ROLES.moderator,
                )
            )
            .annotate(num_flags=Count("flag", distinct=True))
            .values_list("id", "num_flags")
        )

    def get_messages_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_messages=Count(
                    "message",
                    filter=Q(
                        message__recipient=self.request.user,
                        message__read__isnull=True,
                        message__sender__pk__in=self.get_available_users(),
                        message__sender__membership__active=True,
                        message__sender__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_messages")
        )

    def get_join_requests_count(self):
        return dict(
            self.get_member_communities()
            .filter(membership__role=Membership.ROLES.admin)
            .annotate(
                num_join_requests=Count(
                    "joinrequest",
                    filter=Q(joinrequest__status=JoinRequest.STATUS.pending),
                    distinct=True,
                )
            )
            .values_list("id", "num_join_requests")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "counters": {
                    "drafts": self.get_drafts_count(),
                    "flags": self.get_flags_count(),
                    "join_requests": self.get_join_requests_count(),
                    "messages": self.get_messages_count(),
                    "notifications": self.get_notifications_count(),
                },
                "roles": Membership.ROLES,
            }
        )
        return data


community_list_view = CommunityListView.as_view()
