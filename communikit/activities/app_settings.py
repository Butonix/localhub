from django.conf import settings

DEFAULT_PAGE_SIZE = getattr(
    settings, "COMMUNIKIT_ACTIVITIES_PAGE_SIZE", 15
)
