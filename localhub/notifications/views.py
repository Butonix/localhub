# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import json

# Django
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View

# Localhub
from localhub.communities.views import CommunityRequiredMixin
from localhub.views import SuccessActionView, SuccessDeleteView, SuccessView

# Local
from .models import Notification, PushSubscription
from .signals import notification_read


class NotificationQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Notification.objects.for_community(self.request.community).for_recipient(
            self.request.user
        )


class UnreadNotificationQuerySetMixin(NotificationQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().unread()


class NotificationSuccessRedirectMixin:
    success_url = reverse_lazy("notifications:list")


class NotificationListView(NotificationQuerySetMixin, ListView):
    paginate_by = settings.LONG_PAGE_SIZE
    template_name = "notifications/notification_list.html"
    model = Notification

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude_blocked_actors(self.request.user)
            .prefetch_related("content_object")
            .select_related("actor", "content_type", "community", "recipient")
            .order_by("is_read", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "is_unread_notifications": self.get_queryset()
                .filter(is_read=False)
                .exists(),
                "webpush_settings": {
                    "public_key": settings.VAPID_PUBLIC_KEY,
                    "enabled": settings.WEBPUSH_ENABLED,
                },
            }
        )
        return data


notification_list_view = NotificationListView.as_view()


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessView,
):
    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        [
            notification_read.send(
                sender=notification.content_object.__class__,
                instance=notification.content_object,
            )
            for notification in qs.prefetch_related("content_object")
        ]
        qs.update(is_read=True)
        return self.success_response()


notification_mark_all_read_view = NotificationMarkAllReadView.as_view()


class NotificationMarkReadView(UnreadNotificationQuerySetMixin, SuccessActionView):
    is_success_ajax_response = True

    def post(self, request, *args, **kwargs):
        self.object.is_read = True
        self.object.save()

        notification_read.send(
            sender=self.object.content_object.__class__,
            instance=self.object.content_object,
        )
        return self.success_response()


notification_mark_read_view = NotificationMarkReadView.as_view()


class NotificationMarkReadRedirectView(
    NotificationSuccessRedirectMixin, NotificationMarkReadView
):
    is_success_ajax_response = False


notification_mark_read_redirect_view = NotificationMarkReadRedirectView.as_view()


class NotificationDeleteAllView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessView
):
    def delete(self, request):
        self.get_queryset().delete()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request):
        return self.delete(request)


notification_delete_all_view = NotificationDeleteAllView.as_view()


class NotificationDeleteView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessDeleteView
):

    ...


notification_delete_view = NotificationDeleteView.as_view()


class BasePushSubscriptionView(CommunityRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            json_body = json.loads(request.body.decode("utf-8"))

            data = {"endpoint": json_body["endpoint"]}
            keys = json_body["keys"]
            data["auth"] = keys["auth"]
            data["p256dh"] = keys["p256dh"]

        except (ValueError, KeyError):
            return HttpResponseBadRequest()

        return self.handle_action(request, **data)

    def handle_action(self, request, auth, p256dh, endpoint):
        raise NotImplementedError


class ServiceWorkerView(TemplateView):
    """
    Returns template containing serviceWorker JS, can't use
    static as must always be under domain. We can also pass
    in server specific settings.
    """

    template_name = "notifications/service_worker.js"

    def get(self, request):
        response = super().get(request)
        response["Content-Type"] = "application/javascript"
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["vapid_public_key"] = settings.VAPID_PUBLIC_KEY
        return data


service_worker_view = ServiceWorkerView.as_view()


class SubscribeView(BasePushSubscriptionView):
    def handle_action(self, request, auth, p256dh, endpoint):

        try:
            PushSubscription.objects.get_or_create(
                auth=auth,
                p256dh=p256dh,
                endpoint=endpoint,
                user=request.user,
                community=request.community,
            )
        except IntegrityError:
            pass  # dupe, ignore

        return JsonResponse({"message": "ok"}, status=201)


subscribe_view = SubscribeView.as_view()


class UnsubscribeView(BasePushSubscriptionView):
    def handle_action(self, request, auth, p256dh, endpoint):

        PushSubscription.objects.filter(
            auth=auth,
            p256dh=p256dh,
            endpoint=endpoint,
            user=request.user,
            community=request.community,
        ).delete()

        return JsonResponse({"message": "ok"}, status=200)


unsubscribe_view = UnsubscribeView.as_view()