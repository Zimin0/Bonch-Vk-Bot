from django.apps import apps
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response

from teams.models import Team, TeamInvites
from teams.serializers import (CreateTeamSerializer, DetailTeamSerializer,
                               SummaryTeamSerializer, UpdateTeamSerializer,
                               UserVisibleTeamsSerializer,
                               TeamInvitesSerializer)

User = apps.get_model("users", "User")
Game = apps.get_model("games", "Game")


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.filter(archived=False).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("game", "captain", "players", "players_count",
                        "name")

    def get_serializer_class(self):
        if self.action == "list":
            return SummaryTeamSerializer
        if self.action == "create":
            return CreateTeamSerializer
        if self.action == "update":
            return UpdateTeamSerializer
        return DetailTeamSerializer

    def create(self, request, **_kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save()
        team.players.add(team.captain)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, *_args, **_kwargs):
        team = self.get_object()
        team.archived = True
        team.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class UserVisibleTeamsViewSet(viewsets.ModelViewSet):
    serializer_class = UserVisibleTeamsSerializer
    queryset = Team.objects.filter(~Q(players_count=1), archived=False).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("game", "captain", "players", "players_count")


class TeamInvitesViewSet(viewsets.ModelViewSet):
    queryset = TeamInvites.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("team", "user", )
    serializer_class = TeamInvitesSerializer
