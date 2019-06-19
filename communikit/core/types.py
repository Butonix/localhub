# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Callable, Dict, List, Tuple

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

HttpRequestResponse = Callable[[HttpRequest], HttpResponse]

ContextDict = Dict[str, Any]

BreadcrumbList = List[Tuple[str, str]]

QuerySetDict = Dict[str, QuerySet]
QuerySetList = List[QuerySet]
