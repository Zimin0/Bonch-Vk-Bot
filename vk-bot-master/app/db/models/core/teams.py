import logging

from app.db import utils
from app.db.models import core
from app.db.models.local import User as LocalUser
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN

logger = logging.getLogger(__name__)


class Team(utils.BaseModel):
    URL = CORE_API_URL + "teams/"
    TTL = utils.Time.MINUTES_15
    CACHING = True

    players: list
    captain: object
    string_name_players: list

    def __init__(self, data, cached=True):
        super().__init__(data, cached)
        self.players = []
        self.captain = None
        self.string_name_players = []

    @utils.client_exception_wrapper
    async def get_players(self, session, including_cap=True):
        if self.captain is None:
            await self.get_captain(session)
        for player_id in self.data["players"]:
            player = await core.User.find_by_id(player_id, session)
            if not including_cap and self.captain.id == player.id:
                continue
            self.players.append(player)
        return self.players

    @utils.client_exception_wrapper
    async def disband(self, session):
        await session.delete(f"{self.URL}{self.data['id']}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                })

    @utils.client_exception_wrapper
    async def kick_player(self, session, player_id):
        self.data["players"].remove(player_id)
        async with session.patch(
            f"{self.URL}{self.data['id']}/",
            data={"players": self.data["players"]}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            team = await response.json()
            return Team(team)

    @utils.client_exception_wrapper
    async def add_player(self, session, player_id):
        self.data["players"].append(player_id)
        async with session.patch(
            f"{self.URL}{self.data['id']}/",
            data={"players": self.data["players"]}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            team = await response.json()
            return Team(team)

    @utils.client_exception_wrapper
    async def new_captain(self, session, player_id):
        self.data["captain"] = player_id
        async with session.patch(
            f"{self.URL}{self.data['id']}/",
            data={"captain": self.data["captain"]}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            team = await response.json()
            return Team(team)

    @utils.client_exception_wrapper
    async def get_captain(self, session):
        if self.captain:
            return self.captain
        self.captain = await core.User.find_by_id(
            self.data["captain"], session
        )
        return self.captain

    async def get_string_name_players(self, state):
        players = await self.get_players(state.aiohttp_session)
        captain = await self.get_captain(state.aiohttp_session)
        for player in players:
            player_name = f"({player.first_name} {player.last_name})"
            if 'platform' in self.data:
                if self.data['platform'] == 'Steam':
                    if 'Steam' in player.data['game_acc']:
                        player_name = f"({player.data['game_acc']['Steam']})"
            if player.id == captain.data["id"]:
                player_name += f" ⭐"

            if player.verified:
                player_name += " ✔"

            player_local = await LocalUser.find_by_core_id(
                state, player.data["id"]
            )
            if player_local:
                user_name = (
                    f"@id{player_local.vk_id}{player_name}"
                )
                self.string_name_players.append(user_name)
            else:
                self.string_name_players.append(player_name)
        return self.string_name_players


class Teams(utils.BaseListModel):
    URL = CORE_API_URL + "teams/"
    TTL = utils.Time.MINUTES_5
    CACHING = True


class TeamInvites(utils.BaseModel):
    URL = CORE_API_URL + "teams/invites/"
    TTL = utils.Time.MINUTES_5
    CACHING = True

    @utils.client_exception_wrapper
    async def set_checked(self, session):
        self.data["type"] = 2
        async with session.patch(
            f"{self.URL}{self.data['id']}/",
            data={"type": self.data["type"]}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            invite = await response.json()
            return TeamInvites(invite)
