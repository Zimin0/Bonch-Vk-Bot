import itertools
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from teams.models import Team
from users.models import User


class Tournament(models.Model):
    DOUBLE = 2
    SINGLE = 1
    STATUSES = (
        (SINGLE, "single elimination"),
        (DOUBLE, "double elimination"),
    )
    name = models.CharField(
        max_length=250, verbose_name="Название турнира", null=False
    )
    description = models.TextField(
        max_length=1500, verbose_name="Описание турнира", null=True
    )
    game = models.ForeignKey(
        "games.Game",
        verbose_name="Игра турнира",
        related_name="game_tournament",
        null=False,
        on_delete=models.CASCADE,
    )
    number_teams_match = models.IntegerField(
        verbose_name="Количество команд в каждом матче на этом турнире",
        default=2,
        validators=[MinValueValidator(2), MaxValueValidator(200)]
    )
    min_teams = models.IntegerField(
        verbose_name="Минимальное количество участников",
        default=2,
    )
    max_teams = models.IntegerField(
        verbose_name="Максимальное количество участвноков",
        default=1000,
    )
    count_wins_in_match = models.IntegerField(
        verbose_name="Необходимое количество побед в раундах,"
                     " для победы в матче",
        default=2,
    )
    grid = models.IntegerField(
        "Сетка",
        choices=STATUSES,
        default=SINGLE
    )
    educational_type_limit = models.ForeignKey(
        "users.EducationalType",
        verbose_name="Ограничение по типу учебного заведения",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    location_limit = models.ManyToManyField(
        "users.Location",
        verbose_name="Ограничение по географическому расположению",
        blank=True,
    )
    federal_districts_limit = models.ManyToManyField(
        "users.FederalDistricts",
        verbose_name="Ограничение по географическому расположению "
                     "(федиральный округ)",
        blank=True,
    )
    registered_teams = models.ManyToManyField(
        "teams.Team",
        verbose_name="Зарегистрированные команды",
        related_name="registered_teams",
        blank=True,
    )
    confirmed_teams = models.ManyToManyField(
        "teams.Team",
        verbose_name="Команды подтвердившие участие",
        related_name="confirmed_teams",
        blank=True,
    )
    allowed_quantity_players_in_team = models.IntegerField(
        verbose_name="Допустимое количество игроков в команде",
        null=False,
        default=5,
    )
    winner = models.ForeignKey(
        "teams.Team",
        verbose_name="Победитель",
        related_name="tournament_winner",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    referee = models.ManyToManyField(
        "users.User",
        verbose_name="Судьи туринира",
        related_name="tournament_referee",
        blank=False,
    )
    study_team = models.BooleanField(
        "Участвовать могут только сборные учебных заведений",
        default=False
    )
    archived = models.BooleanField(verbose_name="Архивирована", default=False)

    def is_team_playing(self, team):
        matches = self.matches.all()
        for match in matches:
            if team in match.teams and not match.winner:
                return True
        return False

    def registration_users(self):
        registration_teams = self.registered_teams.all()
        res = []
        for team in registration_teams:
            res.extend(list(team.players.all()))
        return res

    def confirmed_users(self):
        confirmed_teams = self.confirmed_teams.all()
        res = []
        for team in confirmed_teams:
            if self.is_team_playing(team):
                res.extend(list(team.players.all()))
        return res

    def get_referee(self):
        for referee in itertools.cycle(self.referee.all()):
            yield referee

    def __str__(self):
        return f"{self.name}"


class TournamentNotification(models.Model):
    REGISTRATION = 1
    PLAYING = 2
    NONE = 3
    STATUSES = (
        (REGISTRATION, "Зарегестрированным"),
        (PLAYING, "Играющим"),
        (NONE, "Не рассылать"),
    )
    users_status = models.IntegerField(
        "Кому",
        choices=STATUSES,
        default=NONE
    )
    text = models.CharField(
        max_length=5000, null=False, verbose_name="Текст уведомления"
    )
    tournament = models.ForeignKey(
        Tournament,
        verbose_name="Турнир",
        related_name="tournament_notification",
        null=True,
        on_delete=models.CASCADE,
    )
    date_created = models.DateTimeField(
        verbose_name="Дата создания уведомления",
        null=False,
        default=datetime.utcnow,
    )
    send = models.BooleanField(
        "Разослать",
        default=False,
    )

    def __repr__(self):
        return f"<Notification {self.text} user_status - {self.users_status}>"

    def __str__(self):
        return f"{self.text} - {self.users_status}"


class TournamentEvent(models.Model):
    HAPPENING = 3
    CONFIRMATION = 2
    REGISTRATION = 1
    STATUSES = (
        (HAPPENING, "Начало турнира"),
        (CONFIRMATION, "Подтверждения"),
        (REGISTRATION, "Регистрации"),
    )
    type = models.IntegerField("тип", choices=STATUSES, default=REGISTRATION)
    time_start = models.DateTimeField(verbose_name="Время начала", null=True)
    time_end = models.DateTimeField(verbose_name="Время завершения", null=True)
    tournament = models.ForeignKey(
        Tournament,
        verbose_name="Турнир",
        related_name="tournament_event",
        null=True,
        on_delete=models.CASCADE,
    )
    send_notification = models.BooleanField(
        "Разослать уведомления",
        default=False
    )

    def __str__(self):
        return f"{self.tournament} - {self.type}: {self.time_start}"


class Match(models.Model):
    WINNER = 3
    LOSER = 2
    STATUSES = (
        (WINNER, "Верхняя сетка"),
        (LOSER, "Нижняя сетка"),
    )
    type = models.IntegerField("тип", choices=STATUSES, default=WINNER)
    date_created = models.DateTimeField(verbose_name="Время проведения")
    tournament = models.ForeignKey(
        Tournament,
        verbose_name="Турнир",
        related_name="matches",
        null=True,
        on_delete=models.CASCADE,
    )
    quantity_wins = models.IntegerField(
        verbose_name="Количество побед в раундах", null=False, default=1
    )
    number = models.IntegerField(
        verbose_name="Этап", default=0
    )
    next_match_for_winner = models.ForeignKey(
        "tournaments.Match",
        verbose_name="Следующий матч для победителя",
        related_name="previous_winner_match",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    next_match_for_loser = models.ForeignKey(
        "tournaments.Match",
        verbose_name="Следующий матч для проигравшего",
        related_name="previous_loser_match",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    referee = models.ForeignKey(
        "users.User",
        verbose_name="Судья матча",
        related_name="match_referee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    archived = models.BooleanField(
        verbose_name="Архивировано", default=False
    )

    @property
    def previous_matches(self):
        previous_match_l = list(self.previous_loser_match.all())
        previous_match_w = list(self.previous_winner_match.all())
        return previous_match_l + previous_match_w

    @property
    def teams(self):
        res = []
        for i in self.rounds_match.order_by('-id').all():
            for k in i.teams.all():
                if k not in res:
                    res.append(k)
        return res

    @property
    def winner(self):
        teams = {team: 0 for team in self.teams}
        teams[None] = self.quantity_wins - 1
        for i in self.rounds_match.all():
            if i.winner in teams:
                teams[i.winner] += 1
        max_val = max(teams.values())
        winner = list({k: v for k, v in teams.items() if v == max_val}.keys())
        return winner[0] if not winner[0] else winner[0].id

    @property
    def winner_name(self):
        return Team.objects.filter(id=self.winner).first()

    @property
    def is_playing(self):
        res = [i.winner for i in self.rounds_match.all() if i.winner]
        if len(res) >= self.quantity_wins:
            for i in range(self.tournament.number_teams_match):
                if res.count(list(set(res))[i]) >= self.quantity_wins:
                    return True
        return False

    @property
    def admin_name(self):
        return f"{self.number}_{self.id}"

    def __str__(self):
        return f"{self.number}_{self.id}"


class Round(models.Model):
    number = models.IntegerField(verbose_name="Номер раунда в матче")
    date_created = models.DateTimeField(verbose_name="Время проведения")
    teams = models.ManyToManyField(
        "teams.Team", verbose_name="Команды матча", related_name="rounds"
    )
    match = models.ForeignKey(
        Match,
        verbose_name="Матч",
        related_name="rounds_match",
        null=False,
        on_delete=models.CASCADE,
    )
    winner = models.ForeignKey(
        "teams.Team",
        verbose_name="Победитель",
        related_name="rounds_winner",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @property
    def team_names(self):
        return " | ".join([team.name for team in list(self.teams.all())])

    def __str__(self):
        return (
            f"{self.match}|round_{self.number}|"
        )


class CsgoMap(models.Model):
    name = models.CharField(verbose_name="название карты", max_length=100)
    server_command = models.CharField(
        verbose_name="команда для сервера", max_length=100
    )

    def __str__(self):
        return (
            f"{self.name}"
        )


class CsgoPeakStage(models.Model):
    match = models.ForeignKey(Match,
                              verbose_name="матч",
                              on_delete=models.CASCADE,
                              related_name="peak_stage")
    selected = models.BooleanField(
        verbose_name="пикнули/забанили", null=False
    )
    map = models.ForeignKey(CsgoMap,
                            verbose_name='карта',
                            on_delete=models.CASCADE)
    team = models.ForeignKey(Team,
                             verbose_name="команда",
                             on_delete=models.CASCADE,
                             null=True)

    def __str__(self):
        return (
            f"{self.match}|{'peak' if self.selected else 'ban'}|"
            f"{self.team}|{self.map.name}"
        )

    def __repr__(self):
        return (
            f"{self.match}|{'peak' if self.selected else 'ban'}|"
            f"{self.team}|{self.map.name}"
        )


class CsgoRound(Round):
    round_map = models.ForeignKey(
        CsgoMap,
        verbose_name="карта раунда",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.match and self.match.tournament:
            if self.match.tournament.game.name != 'CS GO':
                raise ValidationError(
                    'Это раунд может быть только в турнире по CS GO'
                )
        super().save(force_insert, force_update, using, update_fields)
