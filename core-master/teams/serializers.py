from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .models import Team, TeamInvites


class SummaryTeamSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "game", "platform", "platform",)


class DetailTeamSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)
    allow_chang = serializers.BooleanField(read_only=True)

    class Meta:
        model = Team
        fields = "__all__"

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        update_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                update_fields.append(attr)
                setattr(instance, attr, value)

        instance.save(update_fields=update_fields)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class CreateTeamSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = ("id", "name", "game", "captain", "players_count",
                  "platform",)

    def validate(self, data):
        if (3 > len(data["name"]) < 12) or set("!»№;%:?*()_+=,") & set(
                data["name"]
        ):
            raise serializers.ValidationError(
                "the name must contain from 3 to 12"
                " characters without using !»№;%:?*()_+=,"
            )
        return data


class UpdateTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "game", "captain", "players", "platform",)


class UserVisibleTeamsSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = ("name", "id", "game", "players_count", "platform",)


class TeamInvitesSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    team_name = serializers.CharField(read_only=True)

    class Meta:
        model = TeamInvites
        fields = ("id", "team", "user", "type", "expired", "team_name",)
