# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from bfg.apps.activities.views.streams import activity_stream_view
from bfg.apps.communities.views import (
    community_list_view,
    community_not_found_view,
    community_sidebar_view,
    community_welcome_view,
)
from bfg.apps.users.views import dismiss_notice_view, user_delete_view, user_update_view

urlpatterns = [
    # Local
    path("", view=activity_stream_view, name="activity_stream"),
    path("", include("bfg.apps.activities.urls")),
    path("bookmarks/", include("bfg.apps.bookmarks.urls")),
    path("comments/", include("bfg.apps.comments.urls")),
    path("events/", include("bfg.apps.events.urls")),
    path("flags/", include("bfg.apps.flags.urls")),
    path("invites/", include("bfg.apps.invites.urls")),
    path("join-requests/", include("bfg.apps.join_requests.urls")),
    path("notifications/", include("bfg.apps.notifications.urls")),
    path("favorites/", include("bfg.apps.likes.urls")),
    path("messages/", include("bfg.apps.private_messages.urls")),
    path("photos/", include("bfg.apps.photos.urls")),
    path("polls/", include("bfg.apps.polls.urls")),
    path("posts/", include("bfg.apps.posts.urls")),
    path("people/", include("bfg.apps.users.urls")),
    path("community/", include("bfg.apps.communities.urls")),
    path("tags/", include("bfg.apps.hashtags.urls")),
    path("communities/", community_list_view, name="community_list"),
    path("account/~update", user_update_view, name="user_update"),
    path("account/~delete", user_delete_view, name="user_delete"),
    path("welcome/", view=community_welcome_view, name="community_welcome"),
    path("sidebar/", view=community_sidebar_view, name="community_sidebar"),
    path("not-found/", view=community_not_found_view, name="community_not_found"),
    path("~dismiss-notice/<str:notice>/", dismiss_notice_view, name="dismiss_notice"),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

# silk
if "silk" in settings.INSTALLED_APPS:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

if settings.DEBUG:

    # debug toolbar
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

    # static views
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # allow preview/debugging of error views in development
    urlpatterns += [
        path("errors/400/", TemplateView.as_view(template_name="400.html")),
        path("errors/403/", TemplateView.as_view(template_name="403.html")),
        path("errors/404/", TemplateView.as_view(template_name="404.html")),
        path("errors/405/", TemplateView.as_view(template_name="405.html")),
        path("errors/500/", TemplateView.as_view(template_name="500.html")),
        path("errors/csrf/", TemplateView.as_view(template_name="403_csrf.html")),
    ]