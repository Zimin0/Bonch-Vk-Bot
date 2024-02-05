import itertools

from django.utils import timezone as dt

from tournaments.models import Match, Round


class MatchDoubleGrid:

    def __init__(self, tournament, match_id):
        self.id = match_id
        self.tournament = tournament
        self.previous_matches = []
        self.match_from_winner = []
        self.match_from_loser = []
        self.match_for_winner = None
        self.match_for_loser = None
        self.type = None
        self.teams = []
        self.delete = False
        self.db_match = None

    def delete_match(self):
        self.delete = True

    def add_team(self, team):
        if len(self.teams) < 2:
            self.teams.append(team)

    def create_rounds(self):
        rounds = self.db_match.rounds_match.all()
        count_rounds = self.tournament.tournament_obj.count_wins_in_match
        for count in range((count_rounds * 2) - 1):
            if len(rounds) < count_rounds:
                match_round = Round(
                    number=count + 1,
                    match=self.db_match,
                    date_created=dt.now()
                )
                match_round.save()
                for team in self.teams:
                    if team == 'Free':
                        match_round.match.archived = True
                        match_round.match.save()
                        continue
                    match_round.teams.add(team)

    def save_match(self):
        if self.match_for_loser:
            match_type = Match.WINNER
        else:
            match_type = Match.LOSER

        db_match = Match(
            tournament=self.tournament.tournament_obj,
            quantity_wins=self.tournament.tournament_obj.count_wins_in_match,
            number=self.get_stage,
            date_created=dt.now(),
            referee=next(self.tournament.referee),
            type=match_type,
        )
        db_match.save()
        self.db_match = db_match

    def add_relations(self):
        if self.db_match:
            if self.match_for_winner:
                self.db_match.next_match_for_winner = \
                    self.match_for_winner.db_match

            if self.match_for_loser:
                self.db_match.next_match_for_loser = \
                    self.match_for_loser.db_match
            self.db_match.save()

    @property
    def is_full_teams(self):
        return len(self.teams) == 2

    def set_winner_match(self, match):
        if self == match:
            raise TypeError
        if match:
            match.previous_matches.append(self)
            match.match_from_winner.append(self)
        self.match_for_winner = match

    def set_loser_match(self, match):
        if self == match:
            raise TypeError
        match.previous_matches.append(self)
        match.match_from_loser.append(self)
        self.match_for_loser = match

    def get_loser_match(self):
        return self.match_for_loser

    def get_winner_match(self):
        return self.match_for_winner

    @staticmethod
    def return_count_stages(match, count_stage):
        if match.match_for_winner:
            count_stage += 1
            return match.return_count_stages(
                match.match_for_winner,
                count_stage
            )
        return count_stage

    @property
    def get_stage(self):
        return self.return_count_stages(self, 1)

    def __repr__(self):
        if self.teams:
            return f"t_{self.id}_{self.teams}"
        return f"t_{self.id}"


class TournamentDoubleGRid:

    def __init__(self, teams, tournament_obj):
        self.tournament_obj = tournament_obj
        self.teams = teams
        self.matches_winner_bracket = []
        self.matches_loser_bracket = []
        self.count_wins_in_match = tournament_obj.count_wins_in_match
        self.final = None
        self.referee = self.tournament_obj.get_referee()

    def __repr__(self):
        return f"{self.tournament_obj.name}"

    @property
    def count_match_in_winner(self):
        count = len(self.teams)
        while not (count & (count - 1) == 0) and count != 0:
            count += 1
        return count

    @property
    def max_stage(self):
        return max(match.get_stage for match in self.matches_winner_bracket)

    def matches_by_stage(self, stage):
        return [match for match in self.matches_winner_bracket
                if match.get_stage == stage]

    def generation_winner_bracket(self):
        for match_id in range(1, self.count_match_in_winner):
            self.matches_winner_bracket.append(MatchDoubleGrid(self, match_id))
        for match in self.matches_winner_bracket:
            match_index = self.matches_winner_bracket.index(match)
            if match_index != 0:
                parent_id = (match_index - 1) / 2
                try:
                    parent_id = int(parent_id)
                except ValueError:
                    parent_id = int(match_index / 2)
                match.set_winner_match(self.matches_winner_bracket[parent_id])

    def get_loser_matches(self, count, last_stage):
        res = []
        while len(res) < count:
            for match in self.matches_loser_bracket:
                if len(res) < count:
                    if last_stage:
                        if len(match.previous_matches) <= 1:
                            res.append(match)
                            res.append(None)
                    elif len(match.previous_matches) == 0 and \
                            not match.match_for_winner:
                        res.append(match)

        return res

    def get_loser_next_matches(self, count):
        res = []
        for match in self.matches_loser_bracket:
            if len(res) < (2 ** count) / 2:
                if len(match.previous_matches) <= 1:
                    res.append(match)
        return res

    @staticmethod
    def chunks_generators(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i: i + n]

    def generation_loser_bracket(self):
        self.matches_loser_bracket = [
            MatchDoubleGrid(self,
                            match_id + len(self.matches_winner_bracket) + 1)
            for match_id in range(self.count_match_in_winner - 2)
        ]
        for stage_number in range(1, self.max_stage + 1):
            winner_match = self.matches_by_stage(stage_number)
            loser_match_for_stage = self.get_loser_matches(
                len(winner_match) * 2,
                stage_number == self.max_stage
            )
            loser_matches = list(
                self.chunks_generators(loser_match_for_stage, 2)
            )

            next_matches = [None for i in winner_match]
            if stage_number not in (1, self.max_stage):
                next_matches = self.get_loser_next_matches(
                    stage_number - 1,
                )
                next_matches.extend(next_matches)
            loser_matches.reverse()
            for win, los, n_match in zip(winner_match, loser_matches,
                                         next_matches):
                los_up = los[0]
                los_dow = los[-1]
                if los_up and win:
                    win.set_loser_match(los_up)
                if los_up and los_dow:
                    los_dow.set_winner_match(los_up)
                if n_match and los_up:
                    los_up.set_winner_match(n_match)

    def add_teams(self):

        first_stage = self.matches_by_stage(self.max_stage)
        first_stage_loser = [match for match in self.matches_loser_bracket
                             if set(match.previous_matches) & set(first_stage)]
        second_stage = self.matches_by_stage(self.max_stage - 1)
        second_stage_loser = [
            match for match in self.matches_loser_bracket
            if set(match.previous_matches) & set(second_stage)
        ]

        for team, match in zip(self.teams, itertools.cycle(first_stage)):
            match.add_team(team)
        for match in first_stage:
            if not match.is_full_teams:
                match.match_for_winner.add_team(match.teams[0])
                match.add_team('Free')
                match.delete_match()

        for match in first_stage_loser:
            match.previous_matches = [
                w_match for w_match in match.previous_matches
                if not w_match.delete
            ]
            if len(match.previous_matches) == 1:
                match.previous_matches[0].set_loser_match(
                    match.match_for_winner
                )
                match.delete_match()
            if not match.previous_matches:
                match.delete_match()

        for match in second_stage_loser:
            match.previous_matches = [
                w_match for w_match in match.previous_matches
                if not w_match.delete
            ]
            if len(match.previous_matches) == 1:
                match.previous_matches[0].set_loser_match(
                    match.match_for_winner
                )
                match.delete_match()
            if not match.previous_matches:
                match.delete_match()

        self.create_grand_final()
        # self.matches_winner_bracket = [
        #     match for match in self.matches_winner_bracket
        #     if not match.delete
        # ]
        self.matches_loser_bracket = [
            match for match in self.matches_loser_bracket
            if not match.delete
        ]
        for match in self.matches_loser_bracket:
            if not match.match_for_winner:
                match.set_winner_match(self.final)

        for match in self.matches_winner_bracket:
            if not match.match_for_winner:
                match.set_winner_match(self.final)
        self.matches_winner_bracket.append(self.final)

    def create_grand_final(self):
        self.final = MatchDoubleGrid(self, 0)

    def save_grid(self):
        for winner_match in self.matches_winner_bracket:
            winner_match.save_match()
        for loser_match in self.matches_loser_bracket:
            loser_match.save_match()

    def create_match_relations(self):
        for winner_match in self.matches_winner_bracket:
            winner_match.add_relations()
        for loser_match in self.matches_loser_bracket:
            loser_match.add_relations()

    def add_rounds(self):
        for winner_match in self.matches_winner_bracket:
            winner_match.create_rounds()
