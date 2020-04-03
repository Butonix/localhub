# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery.utils.log import get_logger
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from localhub.events import tasks

from .models import Event

celery_logger = get_logger(__name__)


@receiver(post_save, sender=Event, dispatch_uid="events.update_event_coordinates")
def update_event_coordinates(instance, created=False, **kwargs):
    if created or instance.location_tracker.changed():

        def run_task():
            try:
                tasks.update_event_coordinates.delay(instance.id)
            except tasks.update_event_coordinates.OperationalError as e:
                celery_logger.exception(e)

        transaction.on_commit(run_task)
