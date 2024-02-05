from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.filters import UserFilter, GameAccountFilter
from users.models import (UserEducation, GameAccount, Notification,
                          Platform, User, UserNotification, UserRole,
                          UserVerificationRequest, EducationalType, Location)
from users.serializers import (CreateUserNotificationSerializer,
                               EducationalInstitutionSerializer,
                               GameAccountSerializer, NotificationSerializer,
                               PlatformSerializer, UserRoleSerializer,
                               UserSerializer,
                               UserVerificationRequestSerializer,
                               EducationalTypeSerializer, LocationSerializer)
from users.signals import UserNotFound

Team = apps.get_model("teams", "Team")


class EducationalLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = LocationSerializer
    queryset = Location.objects.all().order_by("name")


class EducationalTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = EducationalTypeSerializer
    queryset = EducationalType.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserVerificationRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserVerificationRequestSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("user",)
    queryset = UserVerificationRequest.objects.filter(archived=False).all()


class UserRoleViewSet(viewsets.ModelViewSet):
    serializer_class = UserRoleSerializer
    queryset = UserRole.objects.all()
    filter_class = UserFilter


class EducationalInstitutionViewSet(viewsets.ModelViewSet):
    serializer_class = EducationalInstitutionSerializer
    queryset = UserEducation.objects.all()
    filter_class = UserFilter


class GameAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = GameAccountSerializer
    queryset = GameAccount.objects.all()
    # filter_class = GameAccountFilter

    # pylint: disable=unused-argument
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except UserNotFound as error:
            return Response({"error": str(error)}, status=status.HTTP_200_OK)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self):
        queryset = self.queryset
        if 'user' in self.request.query_params:
            queryset = queryset.filter(
                user__id=self.request.query_params['user'])
        queryset = queryset.all()
        return queryset


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()


class PlatformViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PlatformSerializer
    queryset = Platform.objects.all()


class UserNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = CreateUserNotificationSerializer
    queryset = UserNotification.objects.all()
    filter_class = UserFilter
