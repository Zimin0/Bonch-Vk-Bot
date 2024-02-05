from app.controller import Controller
from app.endpoints import profile, team, tournament
from app.endpoints.main import endpoint as main_endpoint

controller = Controller()
controller.add_endpoint(main_endpoint, as_default=True)

for tournament_endpoint in dir(tournament):
    if "endpoint" in tournament_endpoint:
        controller.add_endpoint(getattr(tournament, tournament_endpoint))

for team_endpoint in dir(team):
    if "endpoint" in team_endpoint:
        controller.add_endpoint(getattr(team, team_endpoint))

for profile_endpoint in dir(profile):
    if "endpoint" in profile_endpoint:
        controller.add_endpoint(getattr(profile, profile_endpoint))
