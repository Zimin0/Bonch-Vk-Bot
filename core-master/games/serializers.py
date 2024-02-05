from rest_framework import serializers

from .models import Game


class GameSerializer(serializers.ModelSerializer):
    platform = serializers.CharField(source="platform.name", read_only=True)
    players_count = serializers.ListField(
        read_only=True
    )

    class Meta:
        model = Game
        fields = ("id", "name", "description", "platform", "players_count")
