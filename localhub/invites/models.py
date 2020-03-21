# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community


class InviteQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(email__in=user.get_email_addresses())

    def pending(self):
        return self.filter(status=self.model.Status.PENDING)

    def accepted(self):
        return self.filter(status=self.model.Status.ACCEPTED)

    def rejected(self):
        return self.filter(status=self.model.Status.REJECTED)


class Invite(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        ACCEPTED = "accepted", _("Accepted")
        REJECTED = "rejected", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=100, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    status_changed = MonitorField(monitor="status")

    sent = models.DateTimeField(null=True, blank=True)

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    objects = InviteQuerySet.as_manager()

    class Meta:
        unique_together = ("email", "community")

    def __str__(self):
        return self.email

    def is_pending(self):
        return self.status == self.Status.PENDING

    def is_accepted(self):
        return self.status == self.Status.ACCEPTED

    def is_rejected(self):
        return self.status == self.Status.REJECTED
