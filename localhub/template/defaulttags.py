# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

register = template.Library()


@register.tag(name="collapsable")
def do_collapsable(parser, token):
    try:
        ignore = template.Variable(token.split_contents()[1])
    except IndexError:
        ignore = False

    nodelist = parser.parse(("endcollapsable",))
    parser.delete_first_token()
    return CollapsableNode(ignore, nodelist)


class CollapsableNode(template.Node):
    def __init__(self, ignore, nodelist):
        self.nodelist = nodelist
        self.ignore = ignore

    def render(self, context):
        content = self.nodelist.render(context)
        if self.ignore:
            try:
                if self.ignore.resolve(context):
                    return content
            except template.VariableDoesNotExist:
                pass
        return template.loader.render_to_string(
            "includes/collapsable.html", {"collapsable_content": content}
        )
