from django.urls import path

from .views import (
    join_request_accept_view,
    join_request_create_view,
    join_request_delete_view,
    join_request_detail_view,
    join_request_list_view,
    join_request_reject_view,
)

app_name = "join_requests"

urlpatterns = [
    path("", view=join_request_list_view, name="list"),
    path("~create/", view=join_request_create_view, name="create"),
    path("<int:pk>/", view=join_request_detail_view, name="detail"),
    path("<int:pk>/~accept/", view=join_request_accept_view, name="accept"),
    path("<int:pk>/~reject/", view=join_request_reject_view, name="reject"),
    path("<int:pk>/~delete/", view=join_request_delete_view, name="delete"),
]
