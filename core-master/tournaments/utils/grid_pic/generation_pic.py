import os

from PIL import Image

from .utils import NewCustom, NewDiagram
from ...models import Match


class TournamentGridPic:

    def __init__(self, tournament):
        self.tournament = tournament
        self.match_ids = list(tournament.matches.order_by('number').all())
        self.grid_pic_name = f"grid_pic_{self.tournament.id}"

    def create_diagram(self):
        if not self.match_ids:
            return None
        grid_name = f"\n\nТурнир: {self.tournament.name}"
        if self.tournament.winner:
            grid_name += f"\t\t\tПобедитель: {self.tournament.winner}"

        with NewDiagram(
                grid_name,
                self.grid_pic_name,
                show=False,
        ):
            final = self.tournament.matches.filter(number=1).first()
            point_name = "Финал" + (" " * 20) + "\n"
            if final.teams:
                match_teams = [f"{team}\n" for team in final.teams]
                point_name += "".join(match_teams)
            else:
                point_name += "\n\n"
            final_match = NewCustom("templates/line_winner.png", point_name)
            self.create_points(final.previous_matches, final_match)
        img_path = f"{self.grid_pic_name}.png"
        img = Image.open(img_path)
        os.remove(img_path)
        return img

    def create_points(self, matches, top_match=None):
        for match in matches:

            if match.type == Match.WINNER:
                previous_matches = match.previous_matches
                line_path = "templates/line_winner.png"
            else:
                previous_matches = [
                    previous_match
                    for previous_match in match.previous_matches
                    if previous_match.type == Match.LOSER
                ]
                line_path = "templates/line_loser.png"

            point_name = str(self.match_ids.index(match)) + (" " * 30) + "\n"
            if match.teams:
                match_teams = [f"{team}\n" for team in match.teams]
                point_name += "".join(match_teams)

            text_previous_matches = []
            if len(previous_matches) <= 1 and len(match.teams) < 2:
                if len(match.teams) == 1:
                    text_previous_matches = [
                        match_t for match_t in match.previous_matches
                        if match.teams[0] in match_t.teams
                    ]
                point_name += "\n".join(
                    [f"Проигравший {self.match_ids.index(item)}"
                     for item in match.previous_matches
                     if item not in previous_matches + text_previous_matches]
                )
            if match.type == 2 and len(match.previous_matches) == 1:
                point_name += '\nFree'
            if match.archived and not match.tournament.winner:
                point_name += 'Free\n'
            if point_name.count("\n") != 3:
                for count in range(3 - point_name.count("\n")):
                    point_name += "\n"

            this_match = NewCustom(line_path, point_name)

            if top_match:
                this_match >> top_match
            if match.previous_matches:
                self.create_points(previous_matches, this_match)
