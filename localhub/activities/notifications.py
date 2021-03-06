# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.notifications.adapter import Adapter, Mailer, Webpusher


class ActivityHeadersMixin:
    HEADERS = [
        ("delete", _("%(actor)s has deleted your %(object)s")),
        ("edit", _("%(actor)s has edited your %(object)s")),
        ("flag", _("%(actor)s has flagged this %(object)s")),
        ("like", _("%(actor)s has liked your %(object)s")),
        ("mention", _("%(actor)s has mentioned you in their %(object)s")),
        (
            "moderator_review",
            _("%(actor)s has submitted or updated their %(object)s for review"),
        ),
        ("followed_user", _("%(actor)s has submitted a new %(object)s")),
        (
            "followed_tag",
            _(
                "Someone has submitted or updated a new %(object)s containing tags you are following"  # noqa
            ),
        ),
        ("reshare", _("%(actor)s has reshared your %(object)s")),
    ]


class ActivityMailer(ActivityHeadersMixin, Mailer):
    def get_subject(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name(),
            "object": self.adapter.object_name,
        }

    def get_template_prefixes(self):
        return super().get_template_prefixes() + ["activities/emails"]


class ActivityWebpusher(ActivityHeadersMixin, Webpusher):
    def get_header(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name(),
            "object": self.adapter.object_name,
        }

    def get_body(self):
        return truncatechars(self.adapter.object.title, 60)


class ActivityAdapter(Adapter):

    ALLOWED_VERBS = [
        "delete",
        "edit",
        "flag",
        "like",
        "mention",
        "followed_user",
        "followed_tag",
        "reshare",
    ]

    mailer_class = ActivityMailer
    webpusher_class = ActivityWebpusher

    def get_template_prefixes(self):
        return super().get_template_prefixes() + ["activities/includes"]
