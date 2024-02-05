from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r"notifications", views.NotificationViewSet)
router.register(r"game_accounts", views.GameAccountViewSet)
router.register(r"verification-request", views.UserVerificationRequestViewSet)
router.register(r"platforms", views.PlatformViewSet)
router.register(
    r"educational-institutions", views.EducationalInstitutionViewSet
)
router.register(
    r"educational-type", views.EducationalTypeViewSet
)
router.register(
    r"educational-location", views.EducationalLocationViewSet
)
router.register(r"roles", views.UserRoleViewSet)
router.register(r"send_notification", views.UserNotificationViewSet)
router.register(r"", views.UserViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
