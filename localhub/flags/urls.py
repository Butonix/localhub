# Django
from django.urls import path

# Local
from .views import flag_delete_view, flag_list_view

app_name = "flags"


urlpatterns = [
    path("", view=flag_list_view, name="list"),
    path("<int:pk>/~delete/", view=flag_delete_view, name="delete"),
]
