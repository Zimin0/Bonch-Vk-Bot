from rest_framework import serializers

from teams.serializers import DetailTeamSerializer
from tournaments.models import Match, Round, Tournament, TournamentEvent, \
    CsgoRound, CsgoMap, CsgoPeakStage
from users.serializers import EducationalTypeSerializer, LocationSerializer, \
    FederalDistrictsSerializer


class TournamentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentEvent
        fields = "__all__"


class TournamentAddTeamSerializer(serializers.Serializer):
    team_id = serializers.IntegerField(write_only=True)


class TournamentSerializer(serializers.ModelSerializer):
    educational_type_limit = EducationalTypeSerializer(read_only=True)
    location_limit = LocationSerializer(read_only=True, many=True)
    federal_districts_limit = FederalDistrictsSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Tournament
        fields = "__all__"


class MatchSerializer(serializers.ModelSerializer):
    teams = DetailTeamSerializer(many=True)
    winner = serializers.IntegerField

    class Meta:
        model = Match
        fields = (
            "id",
            "number",
            "teams",
            "winner",
            "quantity_wins",
            "tournament",
            "type",
        )


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = "__all__"


class CsgoRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsgoRound
        fields = "__all__"


class CsgoMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsgoMap
        fields = (
            "id",
            "name"
        )


class CsgoPeakStageSerializer(serializers.ModelSerializer):
    map_name = serializers.CharField(source="map.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = CsgoPeakStage
        fields = (
            "map",
            "map_name",
            "selected",
            "team",
            "team_name",
            "match"
        )


class SimpleObjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")
    name = serializers.CharField(label="название")


class CsgoPeakQueueItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")
    map = SimpleObjectSerializer()
    team = SimpleObjectSerializer()
    type = serializers.CharField(label="тип")

class CsgoPeakQueueSerializer(serializers.Serializer):
    items = CsgoPeakQueueItemSerializer(many=True)
    next_peak = serializers.IntegerField(label="id следующего пика/бана")


class RefereeInviteSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, label="Ссылка на беседу")
