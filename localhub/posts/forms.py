# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm

from .models import Post
from .opengraph import Opengraph


class PostForm(ActivityForm):

    clear_opengraph_data = forms.BooleanField(
        required=False, label=_("Clear OpenGraph data from post")
    )

    fetch_opengraph_data = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Fetch OpenGraph data from URL if available"),
    )

    class Meta(ActivityForm.Meta):
        model = Post
        fields = (
            "title",
            "additional_tags",
            "url",
            "clear_opengraph_data",
            "fetch_opengraph_data",
            "description",
            "allow_comments",
            "opengraph_image",
            "opengraph_description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["url"].label = _("URL")
        self.fields["title"].help_text = _("Optional if URL provided")
        self.fields["opengraph_image"].widget = forms.HiddenInput()
        self.fields["opengraph_description"].widget = forms.HiddenInput()

        if self.instance.opengraph_image or self.instance.opengraph_description:
            self.initial["fetch_opengraph_data"] = False
            self.fields["fetch_opengraph_data"].label = _(
                "Re-fetch OpenGraph data from URL if available"
            )
        else:
            del self.fields["clear_opengraph_data"]

    def clean(self):
        cleaned_data = super().clean()
        try:
            cleaned_data.update(self.get_opengraph_data(**cleaned_data))
        except Opengraph.Invalid:
            self.add_error("url", _("This URL appears to be invalid."))
            return cleaned_data

        title = cleaned_data.get("title")
        url = cleaned_data.get("url")

        if not any((title, url)):
            raise forms.ValidationError(_("Either title or URL must be provided"))

        return cleaned_data

    def get_opengraph_data(
        self,
        *,
        title="",
        url="",
        fetch_opengraph_data=False,
        clear_opengraph_data=False,
        **cleaned_data
    ):
        if clear_opengraph_data:
            return {"opengraph_image": "", "opengraph_description": ""}

        if not url:
            return {}

        if not title or fetch_opengraph_data:
            og = Opengraph.from_url(url)
            data = {"title": (title or og.title)[:300], "url": og.url}
            if fetch_opengraph_data:
                data.update(
                    {
                        "opengraph_image": og.image or "",
                        "opengraph_description": og.description or "",
                    }
                )
            return data
        return {}
