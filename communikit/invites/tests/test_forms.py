import pytest


from communikit.communities.models import Community, Membership
from communikit.invites.forms import InviteForm
from communikit.invites.tests.factories import InviteFactory


pytestmark = pytest.mark.django_db


class TestInviteForm:
    def test_email_user_already_member(self, member: Membership):
        form = InviteForm(member.community, {"email": member.member.email})
        assert not form.is_valid()

    def test_email_already_sent(self):
        invite = InviteFactory()
        form = InviteForm(invite.community, {"email": invite.email})
        assert not form.is_valid()

    def test_email_ok(self, community: Community):
        form = InviteForm(community, {"email": "tester@gmail.com"})
        assert form.is_valid()
