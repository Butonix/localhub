# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Rulesets for the activities app and subclassed models.
"""

import rules
from localhub.communities.rules import is_member, is_moderator


@rules.predicate
def is_owner(user, activity):
    return user.id == activity.owner_id


@rules.predicate
def is_parent_owner(user, activity):
    if activity.parent:
        return user.id == activity.parent.owner_id
    return False


@rules.predicate
def is_activity_community_member(user, activity):
    return is_member.test(user, activity.community)


@rules.predicate
def is_activity_community_moderator(user, activity):
    return is_moderator.test(user, activity.community)


@rules.predicate
def allows_comments(user, activity):
    return activity.allow_comments


@rules.predicate
def is_reshare(user, activity):
    return activity.is_reshare


is_editor = is_owner | is_activity_community_moderator

rules.add_perm("activities.create_activity", is_member)
rules.add_perm("activities.change_activity", is_editor & ~is_reshare)
rules.add_perm("activities.delete_activity", is_editor)

rules.add_perm(
    "activities.flag_activity",
    is_activity_community_member & ~is_owner & ~is_parent_owner,
)

rules.add_perm("activities.like_activity", is_activity_community_member & ~is_owner)

rules.add_perm(
    "activities.reshare_activity",
    is_activity_community_member & ~is_owner & ~is_parent_owner,
)

rules.add_perm(
    "activities.create_comment", is_activity_community_member & allows_comments
)
