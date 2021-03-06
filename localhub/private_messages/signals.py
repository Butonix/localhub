# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.dispatch import receiver

# Localhub
from localhub.notifications.signals import notification_read

# Local
from .models import Message


@receiver(
    notification_read,
    sender=Message,
    dispatch_uid="localhub.private_messages.message_notification_read",
)
def message_notification_read(instance, **kwargs):
    instance.mark_read()
