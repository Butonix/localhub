# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications import BaseNotificationAdapter, register
from localhub.users.utils import user_display

from .models import Comment


@register(Comment)
class CommentNotificationAdapter(BaseNotificationAdapter):
    NOTIFICATION_HEADERS = {
        "flag": _("%(actor)s has flagged this comment"),
        "like": _("%(actor)s has liked your comment"),
        "mention": _("%(actor)s has mentioned you in their comment"),
        "moderator_review": _("%(actor)s has submitted or updated a comment to review"),
        "new_comment": _("%(actor)s has submitted a comment on one of your posts"),
        "new_sibling": _("%(actor)s has made a comment on a post you've commented on"),
        "reply": _("%(actor)s has replied to your comment"),
        "followed_user": _("%(actor)s has submitted a new comment"),
    }

    def get_notification_header(self):
        return dict(self.NOTIFICATION_HEADERS)[self.verb] % {
            "actor": user_display(self.actor)
        }

    def get_email_subject(self):
        return self.get_notification_header()

    def get_webpush_header(self):
        return self.get_notification_header()

    def get_webpush_body(self):
        return self.object.abbreviate()
