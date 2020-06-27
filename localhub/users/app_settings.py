# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import re

# Django
from django.urls import reverse_lazy

MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")

MENTIONS_TYPEAHEAD_CONFIG = (
    "@",
    reverse_lazy("users:autocomplete_list"),
)
