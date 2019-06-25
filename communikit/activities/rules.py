import rules

from django.conf import settings

from communikit.activities.models import Activity
from communikit.communities.rules import is_member, is_moderator


@rules.predicate
def is_owner(user: settings.AUTH_USER_MODEL, activity: Activity) -> bool:
    return user.id == activity.owner_id


@rules.predicate
def is_activity_community_member(
    user: settings.AUTH_USER_MODEL, activity: Activity
) -> bool:
    return is_member.test(user, activity.community)


@rules.predicate
def is_activity_community_moderator(
    user: settings.AUTH_USER_MODEL, activity: Activity
) -> bool:
    return is_moderator.test(user, activity.community)


is_editor = is_owner | is_activity_community_moderator

rules.add_perm("activities.create_activity", is_member)
rules.add_perm("activities.change_activity", is_editor)
rules.add_perm("activities.delete_activity", is_editor)
rules.add_perm(
    "activities.flag_activity", is_activity_community_member & ~is_owner
)
rules.add_perm(
    "activities.like_activity", is_activity_community_member & ~is_owner
)
