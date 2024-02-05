from django.contrib import admin
from django.urls import include, path
from .settings import DEBUG

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/games/", include("games.urls")),
    path("api/v1/teams/", include("teams.urls")),
    path("api/v1/tournaments/", include("tournaments.urls")),
    path("", include("steam_auth.urls")),
    path("", include("battlenet_auth.urls")),
]

admin.site.site_header = f"CyberBot Admin Panel 1.0"
