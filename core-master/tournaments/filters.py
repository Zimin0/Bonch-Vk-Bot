from django.apps import apps
from django.db.models import Q
from django_filters import rest_framework as filters

from tournaments.models import Match, Tournament

Game = apps.get_model("games", "Game")
User = apps.get_model("users", "User")


class GameFilter(filters.FilterSet):
    game = filters.ModelChoiceFilter(queryset=Game.objects.all())


class TournamentFilter(filters.FilterSet):
    tournament = filters.ModelChoiceFilter(queryset=Tournament.objects.all())


class MatchFilter(filters.FilterSet):
    match = filters.ModelChoiceFilter(queryset=Match.objects.all())


class AllowTournamentsUserFilter(filters.FilterSet):
    q = filters.ModelChoiceFilter(method='user_filter',
                                  queryset=User.objects.all())

    class Meta:
        model = Tournament
        fields = ['q', 'game']

    @staticmethod
    def user_filter(queryset, name, value):
        if not value.educational_institution:
            return queryset.filter(
                Q(federal_districts_limit=None) &
                Q(location_limit=None) &
                Q(educational_type_limit=None)
            )
        federal_districts = value.federal_districts
        location = value.location
        educational_type = value.educational_institution.type
        return queryset.filter(
            Q(
                Q(federal_districts_limit__in=[federal_districts]) &
                Q(location_limit=None) &
                Q(educational_type_limit=None) # 100
            ) |
            Q(
                Q(federal_districts_limit__in=[federal_districts]) &
                Q(location_limit__in=[location]) &
                Q(educational_type_limit=None)
            ) |
            Q(
                Q(federal_districts_limit__in=[federal_districts]) &
                Q(location_limit__in=[location]) &
                Q(educational_type_limit__in=[educational_type])
            ) |
            Q(
                Q(federal_districts_limit=None) &
                Q(location_limit__in=[location]) &
                Q(educational_type_limit__in=[educational_type])
            ) |
            Q(
                Q(federal_districts_limit=None) &
                Q(location_limit=None) &
                Q(educational_type_limit__in=[educational_type])
            ) |
            Q(
                Q(federal_districts_limit__in=[federal_districts]) &
                Q(location_limit=None) &
                Q(educational_type_limit__in=[educational_type])
            ) |
            Q(
                Q(federal_districts_limit=None) &
                Q(location_limit=None) &
                Q(educational_type_limit=None)
            ) |
            Q(
                Q(federal_districts_limit=None) &
                Q(location_limit__in=[location]) &
                Q(educational_type_limit=None)
            )
        ).all()
