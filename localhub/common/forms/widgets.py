# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ClearableImageInput(forms.ClearableFileInput):
    template_name = "includes/forms/widgets/clearable_image.html"


class TypeaheadMixin:

    # typeahead configs should be a pair of (trigger key, url)
    # e.g. [("@", "/mentions/search/"), ] -> the search will be initiated
    # with the key "@" and queries "/mentions/search"

    typeahead_configs = []

    def __init__(self, attrs=None, typeahead_configs=None):
        super().__init__(attrs)
        self.typeahead_configs = typeahead_configs or self.typeahead_configs

    def get_context(self, name, value, attrs):
        data = super().get_context(name, value, attrs)
        # convert to JSON for the JS to handle
        data["typeahead_config"] = json.dumps(
            [{"key": key, "url": str(url)} for (key, url) in self.typeahead_configs]
        )
        return data


class BaseTypeaheadInput(TypeaheadMixin, forms.TextInput):
    """Provides AJAX typeahead functionality.

    Typeahead urls should be provided as tuple:
    (charkey, url)
    e.g.
    ("@", "/users/autocomplete/")
    """

    template_name = "includes/forms/widgets/typeahead.html"

    def format_value(self, value):
        """Replace any commas with space, remove any extra spaces"""
        if not value:
            return value
        return " ".join(value.replace(",", " ").strip().lower().split())


class TypeaheadInput(BaseTypeaheadInput):
    """Default typeahead implementation, with all urls enabled"""

    typeahead_configs = [
        settings.LOCALHUB_HASHTAGS_TYPEAHEAD_CONFIG,
        settings.LOCALHUB_MENTIONS_TYPEAHEAD_CONFIG,
    ]


class CalendarWidget(forms.SplitDateTimeWidget):
    """
    Custom SplitDateTimeWidget using a Javascript-generated
    calendar. Note that the CSS/JS code is bundled as part of the
    project assets and frontend framework and so is not
    included as separate Media assets with this widget.
    """

    template_name = "includes/forms/widgets/calendar.html"
    input_type = "calendar"

    def __init__(self, *args, **kwargs):
        date_attrs = kwargs.pop("date_attrs", {})
        date_attrs.update(
            {
                "data-action": "click->calendar#toggle",
                "data-target": "calendar.dateInput",
                "autocomplete": "off",
                "placeholder": _("DD/MM/YYYY"),
            }
        )

        self.publisher = kwargs.pop("publisher", False)
        self.subscriber = kwargs.pop("subscriber", False)

        time_attrs = kwargs.pop("time_attrs", {})
        time_attrs.update(
            {
                "autocomplete": "off",
                "placeholder": _("HH:MM"),
                "data-target": "calendar.timeInput",
                "type": "time",
            }
        )
        super().__init__(
            date_attrs=date_attrs,
            date_format="%d/%m/%Y",
            time_attrs=time_attrs,
            time_format="%H:%M",
            *args,
            **kwargs
        )

    def get_context(self, name, value, attrs):
        data = super().get_context(name, value, attrs)

        data.update({"publisher": self.publisher, "subscriber": self.subscriber})
        return data
