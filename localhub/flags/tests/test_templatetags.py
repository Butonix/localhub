# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.users.factories import UserFactory

from ..models import Flag
from ..templatetags.flags_tags import get_flags_count

pytestmark = pytest.mark.django_db


class TestGetFlagsCount:
    def test_get_count(self, rf, post):
        Flag.objects.create(
            content_object=post, community=post.community, user=UserFactory()
        )
        req = rf.get("/")
        req.community = post.community
        assert get_flags_count({"request": req}) == 1
