# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.db.models import F
from django.urls import reverse

from ..models import Message

register = template.Library()


@register.inclusion_tag("private_messages/includes/message.html", takes_context=True)
def show_message(
    context,
    user,
    community,
    message,
    show_sender_info=True,
    show_recipient_info=True,
    show_thread_info=True,
    is_detail=False,
):

    is_sender = user == message.sender
    is_recipient = user == message.recipient

    outbox_url = reverse("private_messages:outbox")

    if is_sender:
        sender_url = outbox_url
        recipient_url = reverse("users:messages", args=[message.recipient.username])
    else:
        sender_url = reverse("users:messages", args=[message.sender.username])
        recipient_url = outbox_url

    if message.parent and message.parent.is_visible(user):
        parent = message.parent
    else:
        parent = None

    if show_thread_info and message.thread and message.thread.is_visible(user):
        thread = message.thread
    else:
        thread = None

    can_reply = (
        is_recipient
        and parent is not None
        and user.has_perm("private_messages.create_message", community)
    )

    return {
        "request": context["request"],
        "is_detail": is_detail,
        "is_recipient": is_recipient,
        "is_sender": is_sender,
        "message": message,
        "parent": parent,
        "thread": thread,
        "recipient_url": recipient_url,
        "sender_url": sender_url,
        "other_user": message.get_other_user(user),
        "show_recipient_info": show_recipient_info,
        "show_sender_info": show_sender_info,
        "can_reply": can_reply,
        "post_delete_redirect": outbox_url if is_detail else None,
    }


@register.simple_tag
def get_unread_message_count(user, community):
    """
    Returns a count of the total number of *unread* messages
    for the current user. If user not logged in just returns 0.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        Message.objects.for_community(community)
        .for_recipient(user)
        .exclude_blocked(user)
        .unread()
        .filter(
            sender__membership__community=community,
            sender__membership__active=True,
            sender__is_active=True,
        )
        .count()
    )


@register.simple_tag
def get_unread_external_message_count(user, community):
    """
    Returns count of unread messages *outside* the current community,
    where the user is an active member. If user not logged in returns 0.
    """

    if user.is_anonymous or not community.active:
        return 0
    return (
        Message.objects.for_recipient(user)
        .exclude_blocked(user)
        .unread()
        .filter(
            community__membership__member=user,
            community__membership__active=True,
            community__active=True,
            sender__membership__community=F("community"),
            sender__membership__active=True,
            sender__is_active=True,
        )
        .exclude(community=community)
        .count()
    )
