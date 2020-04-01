# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from urllib.parse import urlparse

import requests
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_urlvalidator = URLValidator()


REL_SAFE_VALUES = "nofollow noopener noreferrer"

IMAGE_EXTENSIONS = (
    "bmp",
    "gif",
    "gifv",
    "jpeg",
    "jpg",
    "pjpeg",
    "png",
    "svg",
    "tif",
    "tiff",
    "webp",
)


def is_https(url):
    """Checks if URL is SSL i.e. starts with https://

    Args:
        url (str)

    Returns:
        bool
    """
    return url and urlparse(url).scheme == "https"


def is_url(url):
    """Checks if a value is a valid URL.

    Args:
        url (str)

    Returns:
        bool
    """

    if url is None:
        return False
    try:
        _urlvalidator(url)
    except ValidationError:
        return False
    return True


def is_image_url(url):
    """Checks if URL points to an image.

    Args:
        url (str)

    Returns:
        bool
    """
    _, ext = os.path.splitext(urlparse(url).path.lower())
    return ext[1:] in IMAGE_EXTENSIONS


def get_domain_url(url):
    """Returns the root domain URL minus path etc. For example:
    http://google.com/abc/ -> http://google.com

    Args:
        url (str)

    Returns:
        str: domain url
    """

    if not is_url(url):
        return url

    parts = urlparse(url)
    return parts.scheme + "://" + parts.netloc


def clean_domain(domain):
    """Removes www. segment of a domain.

    Args:
        domain (str)

    Returns:
        str: cleaned domain
    """
    if domain and domain.startswith("www."):
        return domain[4:]
    return domain


def get_domain(url):
    """Returns domain of URL e.g. http://google.com -> google.com.

    If "www." is present it is removed e.g. www.google.com -> google.com.

    Args:
        url (str): valid URL

    Returns:
        str: domain
    """
    if not is_url(url):
        return url

    return clean_domain(urlparse(url).netloc)


def resolve_url(url):
    """Resolves URL from HEAD and redirects to get the "true" URL.

    Args:
        url (str)

    Returns:
        str: URL. If no HEAD found then returns original URL.
    """
    try:
        response = requests.head(url, allow_redirects=True)
        if response.ok and response.url:
            return response.url
    except (requests.RequestException):
        pass
    return url


def get_filename(url):
    """
    Returns last part of a url e.g. "https://imgur.com/some-image.gif" ->
    "some-image.gif".
    """
    return urlparse(url).path.split("/")[-1]
