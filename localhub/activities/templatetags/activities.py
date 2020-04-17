# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.urls import reverse
from django.utils.translation import gettext as _

from localhub.utils.http import is_https

from ..oembed import bootstrap_oembed
from ..utils import get_activity_querysets, load_objects

register = template.Library()


_oembed_registry = bootstrap_oembed()


@register.simple_tag
def get_pinned_activity(user, community):
    """
    Returns the single pinned activity for this community. If
    no pinned activity returns None.

    Args:
        user (User)
        community (Community)

    Returns:
        Activity or None
    """
    if user.is_anonymous or not community.active:
        return None

    qs, querysets = get_activity_querysets(
        lambda model: model.objects.for_community(community)
        .with_common_annotations(user, community)
        .published()
        .exclude_blocked(user)
        .select_related("owner")
        .filter(is_pinned=True)
    )

    result = qs.first()

    if result is None:
        return None

    return load_objects([result], querysets)[0]


@register.filter
def is_oembed_url(user, url):
    """Determines whether URL is oembed enabled and if
    user has enabled embedding. Any non-https URL is
    also rejected.

    Args:
        user (User)
        url (str)

    Returns:
        bool
    """
    if (
        not url
        or not is_https(url)
        or not user.is_authenticated
        or not user.show_embedded_content
    ):
        return False
    return _oembed_registry.provider_for_url(url) is not None


@register.simple_tag
def resolve_model_url(model, view_name):
    """Determines Activity url view.

    Example:
        {% resolve_model_url Post 'list' %}

    Args:
        model (Activity class): model class
        view_name (str): name of the view

    Returns:
        str: url
    """
    return reverse(f"{model._meta.app_label}:{view_name}")


@register.simple_tag
def resolve_url(activity, view_name):
    """Determines Activity url view.

    Example:
        {% resolve_model_url post 'update' %}

    Args:
        model (Activity):  instance
        view_name (str): name of the view

    Returns:
        str: url
    """
    return activity.resolve_url(view_name)


@register.simple_tag
def verbose_name(activity):
    """
    Verbose single name of model.

    Args:
        activity (Activity or class)

    Returns:
        str
    """
    return _(activity._meta.verbose_name)


@register.simple_tag
def verbose_name_plural(activity):
    """
    Verbose plural name of model.

    Args:
        activity (Activity or class)

    Returns:
        str
    """
    return _(activity._meta.verbose_name_plural)


@register.inclusion_tag("activities/includes/activity.html")
def render_activity(request, user, object, is_pinned=False, **extra_context):
    """Renders a single activity. Determines the correct include template
    based on object type.

    Args:
        request (HttpRequest)
        user (User)
        object (Activity)
        is_pinned (bool, optional): if the "pinned" template is shown
        **extra_context: additional template variables

    Returns:
        dict: context dict
    """

    app_label = object._meta.app_label
    model_name = object._meta.model_name
    if is_pinned:
        template = f"{app_label}/includes/{model_name}_pinned.html"
    else:
        template = f"{app_label}/includes/{model_name}.html"

    if object.parent:
        is_content_sensitive = object.parent.is_content_sensitive(user)
    else:
        is_content_sensitive = object.is_content_sensitive(user)

    return {
        "request": request,
        "user": user,
        "community": object.community,
        "object": object,
        "object_type": model_name,
        "is_content_sensitive": is_content_sensitive,
        "template_name": template,
        model_name: object,
        **extra_context,
    }
