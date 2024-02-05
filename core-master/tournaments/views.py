import time
from itertools import cycle

from django.apps import apps
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from teams.serializers import SummaryTeamSerializer
from tournaments.utils.grid_pic.generation_pic import TournamentGridPic
from users.serializers import (TeamWithCaptainSerializer,
                               UserNotificationSerializer)
from .filters import MatchFilter, TournamentFilter, \
    AllowTournamentsUserFilter
from .models import Match, Round, Tournament, TournamentEvent, CsgoRound, \
    CsgoMap, CsgoPeakStage
from .serializers import (MatchSerializer, RefereeInviteSerializer,
                          RoundSerializer,
                          TournamentEventSerializer,
                          TournamentSerializer, TournamentAddTeamSerializer,
                          CsgoRoundSerializer, CsgoMapSerializer,
                          CsgoPeakStageSerializer, CsgoPeakQueueSerializer)
from .tasks import TournamentGridSingle

Team = apps.get_model("teams", "Team")
UserNotification = apps.get_model("users", "UserNotification")
Notification = apps.get_model("users", "Notification")


class TournamentGridViewSet(mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    authentication_classes = []
    queryset = Tournament.objects.all()

    def retrieve(self, request, *args, **kwargs):
        image_generator = TournamentGridPic(self.get_object())
        image = image_generator.create_diagram()
        if not image:
            return HttpResponse(status=404)
        response = HttpResponse(content_type="image/png")
        image.save(response, "PNG")
        return response


class TournamentViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.filter(archived=False).all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AllowTournamentsUserFilter

    @action(
        methods=["POST"],
        detail=True,
        url_path="register",
        serializer_class=TournamentAddTeamSerializer,
    )
    def register_team(self, request, *args, **kwargs):
        tournament = self.get_object()

        team = Team.objects.filter(id=request.data['team_id']).first()
        if not team:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.registered_teams.add(team)
        tournament.save()

        return Response(
            status=status.HTTP_201_CREATED,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="confirm",
        serializer_class=TournamentAddTeamSerializer,
    )
    def confirm_team(self, request, *args, **kwargs):
        tournament = self.get_object()

        team = Team.objects.filter(id=request.data['team_id']).first()
        if not team:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.confirmed_teams.add(team)
        tournament.save()

        return Response(
            status=status.HTTP_201_CREATED,
        )


class TournamentEventViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentEventSerializer
    queryset = TournamentEvent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TournamentFilter


class CsgoMapViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = CsgoMapSerializer
    queryset = CsgoMap.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TournamentFilter


class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    queryset = Match.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TournamentFilter


class RefereeMatchViewSet(viewsets.ModelViewSet):
    serializer_class = RefereeInviteSerializer
    queryset = Match.objects.all()
    filter_backends = (DjangoFilterBackend,)

    # pylint: disable=unused-argument
    def invite_referee(self, request, *_args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        notification = Notification(
            text=serializer.data["text"],
            type=Notification.PERSONAL,
            system=True
        )
        notification.save()
        user_notification = UserNotification(
            user=self.get_object().referee,
            notification=notification,
        )
        user_notification.save()
        serializer = UserNotificationSerializer(user_notification)
        return Response(serializer.data)


class RoundViewSet(viewsets.ModelViewSet):
    serializer_class = RoundSerializer
    queryset = Round.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MatchFilter

    def update(self, request, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            # pylint: disable=protected-access
            instance._prefetched_objects_cache = {}
        tournament_id = instance.match.tournament.id
        tournament_grid = TournamentGridSingle(tournament_id)
        tournament_grid.update_grid()
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if queryset and queryset[0].match.tournament.game.name == 'CS GO':
            rounds_id = [round_match.id for round_match in queryset]
            csgo_rounds = CsgoRound.objects.filter(id__in=rounds_id).all()
            serializer = CsgoRoundSerializer(csgo_rounds, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CsgoPeakStageViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = CsgoPeakStageSerializer
    queryset = CsgoPeakStage.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MatchFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class CsgoPeakQueueViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = CsgoPeakQueueSerializer
    queryset = Match.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MatchFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        pool = cycle(instance.teams)
        queue_peak = []

        if instance.tournament.count_wins_in_match != 1:
            for peak_type in ('ban', 'ban', 'peak', 'peak', 'ban', 'ban'):
                queue_peak.append((next(pool), peak_type))
        else:
            for peak_type in ('ban', 'ban', 'ban', 'ban', 'ban', 'ban'):
                queue_peak.append((next(pool), peak_type))

        res = {"items": []}
        next_peak = 7
        selected_maps = []
        for item_id, queue_item in enumerate(queue_peak):
            cs_map = CsgoPeakStage.objects.filter(
                match=instance,
                selected=queue_item[1] == 'peak',
                team=queue_item[0],
            ).exclude(id__in=selected_maps).first()
            item = {
                "id": item_id + 1,
                "type": queue_item[1],
                "team": {
                    "id": queue_item[0].id,
                    "name": queue_item[0].name,
                },
            }

            if cs_map and cs_map.id not in selected_maps:

                item['map'] = {
                    "id": cs_map.map.id,
                    "name": cs_map.map.name,
                }
                selected_maps.append(cs_map.id)
            else:
                item['map'] = {
                    "id": None,
                    "name": None
                }

            res["items"].append(item)

            if not item['map']['name']:
                if next_peak > item['id']:
                    next_peak = item['id']

        if len(selected_maps) == 6:
            selected_map_ids = [cs_map.map.id
                                for cs_map in instance.peak_stage.all()]
            cs_map = CsgoMap.objects.exclude(id__in=selected_map_ids).first()
            res["items"].append(
                {'id': 7,
                 'map': {'id': cs_map.id, 'name': cs_map.name},
                 'team': {'id': None, 'name': 'AUTO'},
                 'type': 'peak'}
            )

            peak_map_list_ids = [item['map']['id']
                                 for item in res['items']
                                 if item['type'] == 'peak']
            peak_map_list = iter(CsgoMap.objects.filter(
                id__in=peak_map_list_ids
            ).all())
            for rnd in instance.rounds_match.all():
                cs_rnd = CsgoRound.objects.filter(id=rnd.id).first()
                cs_rnd.round_map = next(peak_map_list)
                cs_rnd.save()

        res["next_peak"] = next_peak
        serializer = CsgoPeakQueueSerializer(res)

        return Response(serializer.data)


class CurrentTeamMatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchSerializer
    queryset = Match.objects.filter(archived=False).all()

    def retrieve(self, *args, **kwargs):
        # pylint: disable=unused-argument
        pk = kwargs.get("pk")
        if not pk or not pk.isdigit():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for match in self.get_queryset():
            match_rounds = match.rounds_match.all()
            if len(match_rounds) == 0 or match.is_playing:
                continue
            for team in match.teams:
                if int(pk) == team.id:
                    serializer = self.get_serializer(match)
                    return Response(serializer.data)
        return Response({})


class CurrentTournamentEventViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentEventSerializer
    queryset = TournamentEvent.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TournamentFilter

    def list(self, *_args, **_kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        tournaments = queryset.all()
        now = timezone.now()
        now_unix = time.mktime(now.timetuple())
        tournaments_res = []
        for i in tournaments:
            time_start = time.mktime(i.time_start.timetuple())
            time_end = time.mktime(i.time_end.timetuple())
            if time_start < now_unix < time_end:
                tournaments_res.append(i)

        serializer = self.get_serializer(tournaments_res, many=True)
        return Response(serializer.data)


class AllowedTeamsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SummaryTeamSerializer
    authentication_classes = []
    queryset = Team.objects.all()

    def list(self, _request, *_args, **kwargs):
        pk = kwargs.get("pk")
        tournament = Tournament.objects.get(id=pk)
        teams = self.get_queryset()
        allowed_teams = []
        for team in teams:
            if ((team.game == tournament.game)
                    and (team.players_count ==
                         tournament.allowed_quantity_players_in_team)):

                captain = team.captain

                if tournament.educational_type_limit or \
                        (tournament.location_limit.exists()) or \
                        (tournament.federal_districts_limit.exists()):
                    if not captain.verified:
                        continue

                if tournament.educational_type_limit:
                    if not (captain.educational_institution.type ==
                            tournament.educational_type_limit):
                        continue

                if tournament.location_limit.exists():
                    if not (
                            captain.location in tournament.location_limit.all()
                    ):
                        continue

                if tournament.federal_districts_limit.exists():
                    if not (
                            captain.federal_districts in
                            tournament.federal_districts_limit.all()
                    ):
                        continue

                allowed_teams.append(team)
        result = self.serializer_class(allowed_teams, many=True)
        return Response(result.data)


class AllowedConfirmTeamsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SummaryTeamSerializer
    authentication_classes = []
    queryset = Team.objects.all()

    def list(self, _request, *_args, **kwargs):
        pk = kwargs.get("pk")
        tournament = Tournament.objects.get(id=pk)
        teams = self.get_queryset()
        allowed_teams = []
        for team in teams:
            users_team = team.players.all()
            user_edu = [user.educational_institution for user in users_team]
            if ((team.game == tournament.game) and
                    (
                            len(users_team) ==
                            tournament.allowed_quantity_players_in_team ==
                            team.players_count
                    )):

                if tournament.game.platform:
                    skip_team = False
                    for user in team.players.all():
                        if tournament.game.platform not in user.platforms.keys():
                            skip_team = True
                    if skip_team:
                        continue

                if tournament.educational_type_limit:
                    if None in user_edu:
                        continue
                    institution_type = {
                        institution.type for institution in user_edu
                    }
                    tournament_edu = {tournament.educational_type_limit}
                    limit = institution_type.difference(tournament_edu)
                    if limit:
                        continue

                if tournament.location_limit.exists():
                    if None in user_edu:
                        continue
                    users_locations = [
                        institution.location for institution in user_edu
                    ]
                    limit = set(
                        tournament.location_limit.all()
                    ).difference(set(users_locations))
                    if not limit:
                        continue

                if tournament.federal_districts_limit.exists():
                    if None in user_edu:
                        continue
                    users_locations = [
                        institution.location for institution in user_edu
                    ]
                    user_federal_district = {
                        location.federal_districts
                        for location in users_locations
                    }
                    t_federal_dist = set(
                        tournament.federal_districts_limit.all()
                    )
                    limit = user_federal_district.difference(t_federal_dist)
                    if limit:
                        continue

                if tournament.study_team:
                    if not team.study_team:
                        continue

                allowed_teams.append(team)
        result = self.serializer_class(allowed_teams, many=True)
        return Response(result.data)


class TournamentTeamsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeamWithCaptainSerializer
    queryset = Tournament

    def create_list_users(self, event, tournament):
        result = []
        teams = []
        if event == 1:
            teams = tournament.registered_teams.all()
        elif event in {2, 3, 4}:
            teams = tournament.confirmed_teams.all()
        for team in teams:
            team = self.serializer_class(team)
            result.append(team.data)
        return result

    def list(
            self,
            *_args,
            **_kwargs,
    ):
        tournament = self.get_object()
        now = timezone.now()
        now_unix = time.mktime(now.timetuple())
        tournament_event = 4
        for event in tournament.tournament_event.all():
            time_start = time.mktime(event.time_start.timetuple())
            time_end = time.mktime(event.time_end.timetuple())
            if time_start < now_unix < time_end:
                tournament_event = event.type

        if tournament_event or tournament.winner:
            result = self.create_list_users(tournament_event, tournament)
            return Response(result)
        return Response([])
