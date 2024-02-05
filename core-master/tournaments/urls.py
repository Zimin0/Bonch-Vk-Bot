from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r"csgo/maps", views.CsgoMapViewSet)
router.register(r"csgo/peak", views.CsgoPeakStageViewSet)
router.register(r"csgo/peak/queue", views.CsgoPeakQueueViewSet)
router.register(r"rounds", views.RoundViewSet)
router.register(r"matches", views.MatchViewSet)
router.register(r"matches/team", views.CurrentTeamMatchViewSet)
router.register(r"events", views.TournamentEventViewSet)
router.register(r"current_events", views.CurrentTournamentEventViewSet)
router.register(r"grid", views.TournamentGridViewSet)
router.register(r"", views.TournamentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/allowed_register_teams",
        views.AllowedTeamsViewSet.as_view({"get": "list"}),
        name="team-list",
    ),
    path(
        "<int:pk>/allowed_confirm_teams",
        views.AllowedConfirmTeamsViewSet.as_view({"get": "list"}),
        name="team-list",
    ),
    path(
        "matches/<int:pk>/referee",
        views.RefereeMatchViewSet.as_view({"post": "invite_referee"}),
        name="referee-retrieve",
    ),
    path(
        "<int:pk>/teams",
        views.TournamentTeamsViewSet.as_view({"get": "list"}),
        name="user-list",
    ),
]
