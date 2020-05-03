# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

from django.utils import timezone

from factory import DjangoModelFactory, Faker, LazyFunction, SubFactory
from factory.fuzzy import FuzzyDateTime

from bfg.apps.communities.factories import CommunityFactory
from bfg.apps.users.factories import UserFactory

from .models import Event


class EventFactory(DjangoModelFactory):
    title = Faker("text")
    description = Faker("text")
    community = SubFactory(CommunityFactory)
    owner = SubFactory(UserFactory)
    published = LazyFunction(timezone.now)

    starts = FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=30),
        end_dt=timezone.now() + timedelta(days=36),
    )

    class Meta:
        model = Event