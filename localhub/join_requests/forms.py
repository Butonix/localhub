# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import forms
from django.utils.translation import gettext as _

from .models import JoinRequest


class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ("intro",)

    def __init__(self, user, community, *args, **kwargs):
        self.user = user
        self.community = community
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        if not self.community.allow_join_requests:
            raise forms.ValidationError(
                _("This community does not allow requests to join.")
            )
        if self.community.members.filter(pk=self.user.id).exists():
            raise forms.ValidationError(_("You are already a member"))

        if self.model.objects.filter(
            sender=self.user, community=self.community
        ).exists():
            raise forms.ValidationError(
                _("You have already requested to join this community")
            )

        if self.community.is_email_blacklisted(self.user.email):
            raise forms.ValidationError(
                _("Sorry, we cannot accept your application to join at this time.")
            )
        return data

    def save(self, commit=True):
        instance = super().save(commit)
        instance.user = self.user
        instance.community = self.community
        if commit:
            instance.save()
        return instance
