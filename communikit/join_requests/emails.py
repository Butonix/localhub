from django.core.mail import send_mail
from django.urls import reverse
from django.template import loader
from django.utils.translation import ugettext as _

from communikit.join_requests.models import JoinRequest


def send_join_request_email(join_request: JoinRequest):
    # tbd: we'll use django-templated-mail at some point
    send_mail(
        _("A request has been received"),
        loader.get_template("join_requests/emails/join_request.txt").render(
            {
                "join_request": join_request,
                "list_url": join_request.community.domain_url(
                    reverse("join_requests:list")
                ),
                "accept_url": join_request.community.domain_url(
                    reverse("join_requests:accept", args=[join_request.id])
                ),
                "reject_url": join_request.community.domain_url(
                    reverse("join_requests:reject", args=[join_request.id])
                ),
            }
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{join_request.community.domain}",
        [u.email for u in join_request.community.get_admins()],
    )


def send_acceptance_email(join_request: JoinRequest):
    # tbd: we'll use django-templated-mail at some point
    send_mail(
        _("Your request has been approved"),
        loader.get_template("join_requests/emails/accepted.txt").render(
            {"join_request": join_request}
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{join_request.community.domain}",
        [join_request.sender.email],
    )


def send_rejection_email(join_request: JoinRequest):
    # tbd: we'll use django-templated-mail at some point
    user = join_request.get_sender()
    send_mail(
        _("Your request has been rejected"),
        loader.get_template("join_requests/emails/rejected.txt").render(
            {"join_request": join_request}
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{join_request.community.domain}",
        [user.email if user else join_request.email],
    )
