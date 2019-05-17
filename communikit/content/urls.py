from django.urls import path

from communikit.content.views import (
    activity_view,
    content_dislike_view,
    content_like_view,
    content_list_view,
    content_search_view,
    post_create_view,
    post_delete_view,
    post_detail_view,
    post_update_view,
    profile_content_list_view,
)

app_name = "content"


urlpatterns = [
    path("", content_list_view, name="list"),
    path("~create/", post_create_view, name="create"),
    path("activity/", activity_view, name="activity"),
    path("search/", content_search_view, name="search"),
    path("profile/<username>/", profile_content_list_view, name="profile"),
    path("post/<int:pk>/", post_detail_view, name="detail"),
    path("post/<int:pk>/~update/", post_update_view, name="update"),
    path("post/<int:pk>/~delete/", post_delete_view, name="delete"),
    path("post/<int:pk>/~like/", content_like_view, name="like"),
    path("post/<int:pk>/~dislike/", content_dislike_view, name="dislike"),
]
