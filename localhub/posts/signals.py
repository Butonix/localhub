# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models.signals import pre_save
from django.dispatch import receiver

from localhub.posts.models import Post


@receiver(
    pre_save, sender=Post, dispatch_uid="posts.fetch_post_metadata_from_url"
)
def fetch_post_metadata_from_url(instance, created=False, **kwargs):
    if created or instance.url_tracker.changed():
        instance.fetch_metadata_from_url(commit=False)
