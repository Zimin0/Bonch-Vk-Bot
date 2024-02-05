from django.apps import apps
from rest_framework import serializers

from users.models import (UserEducation, GameAccount, Notification,
                          Platform, User, UserNotification, UserRole,
                          UserVerificationRequest, EducationalType,
                          Location, FederalDistricts)

Team = apps.get_model("teams", "Team")


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class FederalDistrictsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederalDistricts
        fields = "__all__"


class UserVerificationRequestSerializer(serializers.ModelSerializer):
    archived = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserVerificationRequest
        fields = "__all__"


class EducationalInstitutionSerializer(serializers.ModelSerializer):
    institute = serializers.CharField(source="institute.name", read_only=True)

    class Meta:
        model = UserEducation
        fields = ("location", "type", "id", "institute", )


class EducationalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalType
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    verified = serializers.BooleanField(read_only=True)
    game_acc = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = "__all__"


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = "__all__"


class GameAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAccount
        fields = ("id", "platform", "nick_name", "user", "platform_token")


class TeamWithCaptainSerializer(serializers.ModelSerializer):
    platform = serializers.JSONField

    class Meta:
        model = Team
        fields = ("id", "name", "captain", "platform")


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ("name", "id")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "text", "endpoints", "attachments", "system")


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    core_id = serializers.IntegerField(source="user_id")

    class Meta:
        model = UserNotification
        fields = ("core_id", "notification")

    @classmethod
    def export(cls, notification):
        serializer = cls(notification)
        data = dict(serializer["notification"].value)
        data["core_id"] = serializer.data["core_id"]
        return {k: v for k, v in data.items() if v is not None}


class CreateUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ("id", "user", "notification")
