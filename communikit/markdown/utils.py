import re
import bleach

from typing import Set

from bleach.linkifier import LinkifyFilter

from django.urls import reverse

from markdownx.utils import markdownify as default_markdownify

ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "p",
    "pre",
]

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update({"img": ["alt", "src"]})

cleaner = bleach.Cleaner(
    tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, filters=[LinkifyFilter]
)

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)")


def markdownify(content: str) -> str:
    """
    Drop-in replacement to default MarkdownX markdownify function.

    - Linkifies URLs, @mentions and #hashtags
    - Restricts permitted HTML tags to safer subset

    """
    return cleaner.clean(
        default_markdownify(linkify_hashtags(linkify_mentions(content)))
    )


def extract_mentions(content: str) -> Set[str]:
    """
    Returns set of @mentions in text
    """
    return set(
        [
            mention
            for token in content.split(" ")
            for mention in MENTIONS_RE.findall(token)
        ]
    )


def linkify_mentions(content: str) -> str:
    """
    Replace all @mentions in the text with links to profile page.
    """

    tokens = content.split(" ")
    rv = []
    for token in tokens:
        for mention in MENTIONS_RE.findall(token):
            # url = reverse("content:profile", args=[mention])
            url = f"/profile/{mention}/"
            token = token.replace(
                "@" + mention, f'<a href="{url}">@{mention}</a>'
            )

        rv.append(token)

    return " ".join(rv)


def linkify_hashtags(content: str) -> str:
    """
    Replace all #hashtags in text with links to some tag search page.
    """
    tokens = content.split(" ")
    rv = []
    # TBD: this should prob. be configurable
    search_url = "/search/"
    for token in tokens:

        for tag in HASHTAGS_RE.findall(token):
            url = search_url + f"?hashtag={tag}"
            token = token.replace("#" + tag, f'<a href="{url}">#{tag}</a>')

        rv.append(token)

    return " ".join(rv)
