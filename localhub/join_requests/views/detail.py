# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from vanilla import DetailView

from localhub.communities.views import CommunityAdminRequiredMixin

from ..models import JoinRequest
from .mixins import JoinRequestQuerySetMixin


class JoinRequestDetailView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, DetailView
):
    model = JoinRequest


join_request_detail_view = JoinRequestDetailView.as_view()
