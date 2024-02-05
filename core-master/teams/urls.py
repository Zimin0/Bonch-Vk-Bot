from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r"invites", views.TeamInvitesViewSet)
router.register(r"visible", views.UserVisibleTeamsViewSet)
router.register(r"", views.TeamViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
