# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Code adapted from https://github.com/pehala/markdown-newtab/

from markdown import Extension
from markdown.inlinepatterns import (
    AUTOLINK_RE,
    IMAGE_LINK_RE,
    LINK_RE,
    AutolinkInlineProcessor,
    ImageInlineProcessor,
    LinkInlineProcessor,
)

from localhub.utils.urls import REL_SAFE_VALUES


class SafeImageMixin:
    """
    Only permit images starting with https://
    """

    def handleMatch(self, match, data):
        element, start, end = super().handleMatch(match, data)
        if element is not None:
            if not element.get("src").startswith("https://"):
                return None, None, None
        return element, start, end


class SafeImageInlineProcessor(SafeImageMixin, ImageInlineProcessor):
    ...


class SafeImageExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            SafeImageInlineProcessor(IMAGE_LINK_RE, md), "image_link", 150
        )


class NewTabMixin:
    """
    Ensures any link is opened in a new tab.
    """

    def handleMatch(self, match, data):
        element, start, end = super().handleMatch(match, data)
        if element is not None:
            element.set("target", "_blank")
            element.set("rel", REL_SAFE_VALUES)
        return element, start, end


class NewTabLinkInlineProcessor(NewTabMixin, LinkInlineProcessor):
    ...


class NewTabAutolinkProcessor(NewTabMixin, AutolinkInlineProcessor):
    ...


class NewTabExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(NewTabLinkInlineProcessor(LINK_RE, md), "link", 160)
        md.inlinePatterns.register(
            NewTabAutolinkProcessor(AUTOLINK_RE, md), "autolink", 120
        )
