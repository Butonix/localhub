# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = "localhub.comments"

    def ready(self):
        import localhub.comments.signals  # noqa
