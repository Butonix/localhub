# Copyright (c) 2020 by Dan Jacob

from factory import DjangoModelFactory, Faker, SubFactory

from localhub.apps.users.factories import UserFactory
from localhub.communities.factories import CommunityFactory

from .models import Message


class MessageFactory(DjangoModelFactory):
    message = Faker("text")
    community = SubFactory(CommunityFactory)
    sender = SubFactory(UserFactory)
    recipient = SubFactory(UserFactory)

    class Meta:
        model = Message
