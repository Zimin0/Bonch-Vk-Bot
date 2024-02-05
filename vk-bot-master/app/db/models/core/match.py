import logging

from app.db import Cache
from app.db.models import core
from app.db.utils import BaseModel, Time, client_exception_wrapper
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN, VK_CONF_ID
from app.vk import create_chat, get_invite_link

logger = logging.getLogger(__name__)


class Match(BaseModel):
    URL = CORE_API_URL + "tournaments/matches/"
    CACHING = True
    TTL = Time.MINUTES_3

    def __init__(self, data, cached=True):
        super().__init__(data, cached)
        self.rounds = []
        self.teams = []
        self.match_chat_link = None

    @client_exception_wrapper
    async def get_match_rounds(self, session):
        async with session.get(
            f"{CORE_API_URL}tournaments/rounds/",
                params={"match": self.data["id"]}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            rounds = await response.json()
            self.rounds = [core.Round(t_round) for t_round in rounds]
            return self.rounds

    @client_exception_wrapper
    async def invite_referee(self, session, text):
        async with session.post(
            f"{self.URL}{self.data['id']}/referee",
                data={"text": text}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            notification = await response.json()
            return notification

    async def get_teams_match(self, session):
        if not self.rounds:
            await self.get_match_rounds(session)
        self.teams = [
            await core.Team.find_by_id(id_team, session, False)
            for id_team in self.rounds[0].data["teams"]
        ]
        return self.teams

    def get_link_match_chat_cache(self):
        self.match_chat_link = Cache.get(f"match_chat_{self.data['id']}")
        return self.match_chat_link

    def set_link_match_chat_cache(self, link):
        return Cache.set(f"match_chat_{self.data['id']}", link)

    async def get_or_create_match_chat(self, session):
        self.get_link_match_chat_cache()
        if self.match_chat_link:
            return self.match_chat_link
        teams = await self.get_teams_match(session)
        tournament = await core.Tournament.find_by_id(
            self.data["tournament"], session
        )
        teams_name = " vs ".join(list(i.data["name"] for i in teams))
        chat_title = f"{tournament.data['name']}: {teams_name}"
        peer_id = await create_chat(session, chat_title)
        link = await get_invite_link(session, VK_CONF_ID + peer_id)
        self.set_link_match_chat_cache(link["link"])
        return link["link"]
