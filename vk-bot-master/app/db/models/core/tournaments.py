import logging

from app.db import Cache
from app.db.models import core
from app.db.models.core.games import Games
from app.db.models.local import User as LocalUser
from app.db.utils import (BaseListModel, BaseModel, Time,
                          client_exception_wrapper
                          )
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN

logger = logging.getLogger(__name__)


class Tournament(BaseModel):
    URL = CORE_API_URL + "tournaments/"
    TTL = Time.MINUTES_3
    CACHING = True

    def __init__(self, data):
        super().__init__(data)
        self.players = []
        self.string_name_players = {}
        self.matches = []
        self.stages = {}
        self.current_event = None

    async def get_current_event(self, session):
        return self.current_event \
            if self.current_event is not None \
            else await self._get_current_event(session)

    @client_exception_wrapper
    async def _get_current_event(self, session):
        async with session.get(
                f"{self.URL}current_events/",
                params={
                    "tournament": self.data["id"]
                },
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            self.current_event = await response.json()
            if self.current_event:
                self.current_event = self.current_event[0]
                return self.current_event
            return self.current_event

    @client_exception_wrapper
    async def get_allowed_register_teams(self, session):
        async with session.get(
                f"{self.URL}{self.data['id']}/allowed_register_teams"
                , headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            teams = [core.Team(team) for team in teams]
            return teams

    @client_exception_wrapper
    async def get_allowed_confirm_teams(self, session):
        async with session.get(
                f"{self.URL}{self.data['id']}/allowed_confirm_teams"
                , headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            teams = [core.Team(team) for team in teams]
            return teams

    @client_exception_wrapper
    async def register_team(self, session, team_id):
        async with session.post(
                f"{self.URL}{self.data['id']}/register/",
                data={
                    "team_id": team_id
                }, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return True

    @client_exception_wrapper
    async def confirm_team(self, session, team_id):
        async with session.post(
                f"{self.URL}{self.data['id']}/confirm/",
                data={
                    "team_id": team_id
                }, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return True

    @client_exception_wrapper
    async def get_team_match(self, session, team_id):
        async with session.get(
                f"{self.URL}matches/team/{team_id}/", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            match = await response.json()
            return core.Match(match)

    async def get_string_name_teams(self, state):
        teams = await self.get_players(state.aiohttp_session)
        for count, team in enumerate(teams):
            captain_local = await LocalUser.find_by_core_id(
                state, team.data["captain"]
            )
            if captain_local:
                if '$' in team.name:
                    team.name = team.name.replace('$', '')
                self.string_name_players[team.name] = (
                    f"@id{captain_local.vk_id}({team.name})"
                )
            else:
                self.string_name_players[team.name] = f"{team.name}"
        return self.string_name_players

    @client_exception_wrapper
    async def get_players(self, session):
        async with session.get(
                f"{self.URL}{self.data['id']}/teams", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            for team in teams:
                self.players.append(core.Team(team))
            return self.players

    @client_exception_wrapper
    async def get_matches(self, session):
        async with session.get(
                f"{self.URL}matches/?tournament={self.data['id']}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            matches = await response.json()
            for match in matches:
                self.matches.append(core.Match(match))
            return self.matches

    async def get_stages(self, session):
        if not self.matches:
            await self.get_matches(session)
        for match in self.matches:
            data = match.data
            if data["number"] in self.stages:
                self.stages[data["number"]].append(data)
            else:
                self.stages[data["number"]] = [data]
        return self.stages

    def set_grid(self, grid, time=Time.MINUTES_3):
        return Cache.set(
            f"tournament_grid_{self.data['id']}",
            str(grid),
            time
            )

    def get_grid(self):
        grid = Cache.get(f"tournament_grid_{self.data['id']}")
        if grid:
            return str(grid)
        return grid

    def del_grid(self):
        return Cache.delete(f"tournament_grid_{self.data['id']}")

    async def is_csgo(self, session):
        games = await Games.all(session)
        csgo_id = [game['id'] for game in games.data if
                   game['name'] == 'CS GO']
        if csgo_id and self.data['game'] == csgo_id[0]:
            return True
        return False


class Tournaments(BaseListModel):
    URL = CORE_API_URL + "tournaments/"
    TTL = Time.MINUTES_3
    CACHING = True


class AllowTournaments(BaseListModel):
    URL = CORE_API_URL + "tournaments/"
    TTL = Time.MINUTES_3
    CACHING = True

    @classmethod
    async def get_allow_tournaments(cls, session, user_id):
        async with session.get(f"{cls.URL}?q={user_id}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }) as response:
            data = await response.json()
            return cls(data)
