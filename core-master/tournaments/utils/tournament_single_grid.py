import itertools
import random

from django.utils import timezone as dt

from tournaments import models
from users.models import Notification, UserNotification


class TournamentGridSingle:
    def __init__(self, tournament):
        self.tournament = tournament
        self.teams = list(tournament.confirmed_teams.all())

    def get_referee(self):
        for referee in itertools.cycle(self.tournament.referee.all()):
            yield referee

    def quantity_matches(self):
        res = []
        count_team = 1
        count_teams = int(len(self.teams))
        while True:
            if count_team >= count_teams:
                if res[-1] / count_teams < 1:
                    res[-1] = count_teams - res[-1]
                return res
            res.append(count_team)
            count_team *= 2

    def start_tournament(self):
        if self.tournament.min_teams > \
                len(self.tournament.confirmed_teams.all()):
            notification = Notification(
                text=(f"Турнир {self.tournament.name} отменен, поскольку не "
                      f"набралось достаточное количество участников!"),
                type=Notification.MAILING,
                system=True
            )
            notification.save()
            for user in self.tournament.registration_users():
                user_notification = UserNotification(
                    notification=notification,
                    user=user
                )
                user_notification.save()
            self.tournament.archived = True
            self.tournament.save()
            return False

        number_match = 0
        referees_list = self.get_referee()
        for i in self.quantity_matches():
            number_match += 1
            for _ in range(1, i + 1):
                args = {
                    "quantity_wins": self.tournament.count_wins_in_match,
                    "tournament": self.tournament,
                    "number": number_match,
                    "date_created": dt.now(),
                    "referee": next(referees_list)
                }
                if number_match != 1:
                    next_matches = self.tournament.matches.filter(
                        number=number_match - 1
                    ).all()
                    for next_match in list(next_matches):
                        if (
                                len(next_match.previous_winner_match.all())
                                < self.tournament.number_teams_match
                        ):
                            args["next_match_for_winner"] = next_match
                            break
                models.Match(**args).save()
        return True

    @staticmethod
    def _handle_team_match(count, teams, match):
        team_match = []
        for k in range(count):
            if teams:
                team = random.choice(teams)
                teams.remove(team)
                team_match.append(team)
        for k in range((match.quantity_wins * 2) - 1):
            if match.tournament.game.name != 'CS GO':
                round_match = models.Round(
                    number=k + 1, date_created=dt.now(), match=match
                )
            else:
                round_match = models.CsgoRound(
                    number=k + 1, date_created=dt.now(), match=match
                )

            round_match.save()
            for team in team_match:
                round_match.teams.add(team)

    def primary_draw_of_teams(self):
        quantity_matches = len(self.quantity_matches())
        teams = self.teams.copy()
        for i in reversed(range(1, quantity_matches + 1)):
            for match in list(self.tournament.matches.filter(number=i).all()):
                count_teams_in_match = self.tournament.number_teams_match
                if len(match.previous_matches) > 1:
                    continue
                if len(match.previous_matches) == 1:
                    count_teams_in_match = 1
                self._handle_team_match(count_teams_in_match, teams, match)

    def update_match(self, match, team):
        if len(match.teams) < self.tournament.number_teams_match:
            if len(match.rounds_match.all()) == 0:
                for k in range((match.quantity_wins * 2) - 1):
                    if match.tournament.game.name != 'CS GO':
                        round_match = models.Round(
                            number=k + 1, date_created=dt.now(), match=match
                        )
                    else:
                        round_match = models.CsgoRound(
                            number=k + 1, date_created=dt.now(), match=match
                        )
                    round_match.save()
                    round_match.teams.add(team)
            else:
                for round_match in list(match.rounds_match.all()):
                    if team not in list(round_match.teams.all()):
                        round_match.teams.add(team)

    def update_grid(self):
        for match in list(self.tournament.matches.all()):
            if len(match.rounds_match.all()) == 0:
                continue
            rounds_winner = []
            for match_round in list(match.rounds_match.all()):
                if match_round.winner:
                    rounds_winner.append(match_round.winner)
                    if (
                            rounds_winner.count(match_round.winner)
                            >= match.quantity_wins
                    ):
                        if match.number == 1:
                            self.tournament.winner = match_round.winner
                            self.tournament.save()
                        else:
                            self.update_match(
                                match.next_match_for_winner, match_round.winner
                            )
                            if self.tournament.grid == self.tournament.DOUBLE:
                                if match.next_match_for_loser:
                                    teams = list(match_round.teams.all())
                                    teams.remove(match_round.winner)
                                    loser = teams[0]
                                    if loser:
                                        self.update_match(
                                            match.next_match_for_loser,
                                            loser,
                                        )

