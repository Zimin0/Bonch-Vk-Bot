from django_filters import rest_framework as filters

from .models import User, GameAccount


class UserFilter(filters.FilterSet):
    user = filters.ModelChoiceFilter(queryset=User.objects.all())


class GameAccountFilter(filters.FilterSet):

    class Meta:
        model = GameAccount
        fields = ["user", "platform"]

