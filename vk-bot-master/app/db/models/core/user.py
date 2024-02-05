import logging
import json

from app.db.cache import Cache
from app.db.models import core
from app.db.models.core.educationals import UserVerificationRequest
from app.db.models.local import User as LocalUser
from app.db.models.core.games import Games
from app.db.utils import BaseModel, Time, client_exception_wrapper
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN

logger = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class User(BaseModel):
    URL = CORE_API_URL + "users/"
    TEAMS_URL = CORE_API_URL + "teams/"
    TTL = Time.MINUTES_3
    CACHING = True

    id: int
    first_name: str
    last_name: str
    teams: list
    _vk_id = None

    def __init__(self, data):
        super().__init__(data)
        self.teams = []
        self.visible_teams = []
        self.captain_teams = []

    @classmethod
    @client_exception_wrapper
    async def create(cls, session, data):
        games = await Games.all(session)
        game_ids = [game['id'] for game in games.data]
        data['game_subscription'] = game_ids
        async with session.post(
                cls.URL,
                data=data,
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            data = await response.json()
            return cls(data)

    @client_exception_wrapper
    async def add_vk_id(self, session, vk_id):
        data = {
            "vk_id": vk_id
        }
        async with session.patch(
                f"{self.URL}{self.id}/", data=data, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            data = await response.json()

    @classmethod
    def _find_cached_core_id(cls, vk_id):
        return Cache.get(f"user_vk_{vk_id}")

    @classmethod
    def _set_cached_core_id(cls, vk_id, value):
        return Cache.set(f"user_vk_{vk_id}", value)

    def set_next_state(self, state_name):
        return Cache.set(f"state_key_{self._vk_id}", state_name)

    def set_current_team_id(self, team_id):
        return Cache.set(f"current_team_key_{self._vk_id}", team_id, 3600)

    def get_current_team_id(self):
        team_id = Cache.get(f"current_team_key_{self._vk_id}")
        if team_id:
            return int(team_id)
        return None

    def delete_current_team_id(self):
        return Cache.delete(f"current_team_key_{self._vk_id}")

    def set_current_game_id(self, game_id):
        return Cache.set(f"current_game_key_{self._vk_id}", game_id)

    def get_current_game_id(self):
        game_id = Cache.get(f"current_game_key_{self._vk_id}")
        try:
            return int(game_id)
        except TypeError:
            return None

    def delete_current_game_id(self):
        return Cache.delete(f"current_game_key_{self._vk_id}")

    def set_current_player_count(self, player_count):
        return Cache.set(
            f"current_player_count_key_{self._vk_id}",
            player_count
        )

    def get_current_player_count(self):
        player_count = Cache.get(f"current_player_count_key_{self._vk_id}")
        try:
            return int(player_count)
        except TypeError:
            return None

    def delete_current_player_count(self):
        return Cache.delete(f"current_player_count_key_{self._vk_id}")

    def set_current_team_limit(self, limit):
        return Cache.set(f"current_team_limit_key_{self._vk_id}", limit)

    def get_current_team_limit(self):
        limit = Cache.get(f"current_team_limit_key_{self._vk_id}")
        try:
            return int(limit)
        except TypeError:
            return None

    def delete_current_team_limit(self):
        return Cache.delete(f"current_team_limit_key_{self._vk_id}")

    def delete_all_user_cache(self):
        keys = Cache.get_keys(f"*key_{self._vk_id}")
        keys += Cache.get_keys(f"*{self.id}")
        for key in keys:
            Cache.delete(key)

    def set_vk_id(self, vk_id):
        self._vk_id = vk_id

    @property
    def vk_id(self):
        return self.vk_id

    @classmethod
    async def find_or_create(cls, state):
        core_id = cls._find_cached_core_id(state.message.peer_id)
        if core_id:
            return await cls.find_by_id(core_id, state.aiohttp_session)

        local_user = await LocalUser.find_or_create(state)
        if not local_user.core_id:
            user = await cls.create(state.aiohttp_session, local_user.__dict__)
        else:
            user = await cls.find_by_id(
                local_user.core_id, state.aiohttp_session
            )

        cls._set_cached_core_id(local_user.vk_id, user.id)
        local_user.core_id = user.id
        state.db.commit()
        return user

    async def get_verification_request_from_core(self, session):
        async with session.get(
                f"{self.URL}verification-request/?user={self.id}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            verification_request = await response.json()
            if verification_request:
                return UserVerificationRequest(verification_request[0])
            return None

    async def get_visible_teams_from_core(self, session):
        async with session.get(
                f"{self.TEAMS_URL}visible/?players={self.id}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            for team in teams:
                self.visible_teams.append(core.Team(team, False))
        return self.visible_teams

    @client_exception_wrapper
    async def get_visible_teams(self, session):
        return (
            self.visible_teams
            if self.visible_teams
            else await self.get_visible_teams_from_core(session)
        )

    @client_exception_wrapper
    async def create_notification(self, session, data):
        data["system"] = True
        async with session.post(
                f"{self.URL}notifications/", json=data, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return await response.json()

    @client_exception_wrapper
    async def send_notification(self, session, data):
        notification = await self.create_notification(session, data)
        data = {
            "user": self.id,
            "notification": notification["id"]
        }
        async with session.post(
                f"{self.URL}send_notification/", json=data, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return await response.json()

    @client_exception_wrapper
    async def create_game_account(self, session, data):
        async with session.post(
                f"{self.URL}game_accounts/", json=data, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return await response.json()

    @client_exception_wrapper
    async def get_captain_teams(self, session):
        async with session.get(
                f"{self.TEAMS_URL}?&captain={self.id}&players={self.id}",
                headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            for team in teams:
                self.captain_teams.append(core.Team(team, False))
        return self.captain_teams

    @client_exception_wrapper
    async def get_teams(self, session):
        async with session.get(
                f"{self.TEAMS_URL}?&players={self.id}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            teams = await response.json()
            for team in teams:
                self.teams.append(core.Team(team, False))
        return self.teams

    @client_exception_wrapper
    async def get_game_accounts(self, session):
        async with session.get(
                f"{self.URL}game_accounts/?user={self.id}", headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            return await response.json()

    @client_exception_wrapper
    async def update_edu(self, session, edu_id):
        self.data["educational_institution"] = edu_id
        async with session.patch(
                f"{self.URL}{self.data['id']}/",
                data={
                    "educational_institution": self.data[
                        "educational_institution"]
                }, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            user = await response.json()
            return User(user)

    @client_exception_wrapper
    async def update_game_subscription(self, session):
        async with session.patch(
                f"{self.URL}{self.data['id']}/",
                data={
                    "game_subscription": self.data["game_subscription"]
                }, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            user = await response.json()
            self._del_cached(user['id'])

    @client_exception_wrapper
    async def update_data(self, session):
        data = {
            'registration_sate': self.data['registration_sate']
        }
        async with session.patch(
                f"{self.URL}{self.data['id']}/",
                data=data, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            user = await response.json()
            self._update(user)
