# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.apps.activities.notifications import ActivityAdapter
from localhub.apps.notifications.decorators import register

from .models import Post


@register(Post)
class PostAdapter(ActivityAdapter):
    ...