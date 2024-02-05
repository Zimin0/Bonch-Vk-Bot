from django.apps import apps
from django_filters import rest_framework as filters

Game = apps.get_model("games", "Game")
User = apps.get_model("users", "User")


class GameFilter(filters.FilterSet):
    game_id = filters.ModelChoiceFilter(queryset=Game.objects.all())


class UserTeamsFilter(filters.FilterSet):
    player = filters.ModelChoiceFilter(
        queryset=User.objects.all(), field_name="players"
    )
