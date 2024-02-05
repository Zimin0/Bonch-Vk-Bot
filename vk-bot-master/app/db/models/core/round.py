import logging

from app.db import Cache
from app.db.models import core
from app.db.utils import BaseModel, Time
from app.settings import CORE_API_URL, CORE_AUTH_TOKEN

logger = logging.getLogger(__name__)


class Round(BaseModel):
    URL = CORE_API_URL + "tournaments/rounds/"
    CACHING = True
    TTL = Time.MINUTES_1

    def set_winning_team(self, team_id, team_winner_id):
        Cache.set(
            f"winner_team_key_{self.data['id']}_{team_id}", team_winner_id
        )
        round_winner = Cache.get(f"winner_team_key_{self.data['id']}")
        if round_winner:
            round_winner += f",{team_id}"
            return Cache.set(
                f"winner_team_key_{self.data['id']}", round_winner
            )
        return Cache.set(f"winner_team_key_{self.data['id']}", str(team_id))

    def get_round_winner_votes(self):
        votes = Cache.get(f"winner_team_key_{self.data['id']}")
        if votes:
            return votes.split(",")
        return []

    async def get_winning_team(self, session, team_id):
        team_id = Cache.get(f"winner_team_key_{self.data['id']}_{team_id}")
        if team_id:
            team = await core.Team.find_by_id(team_id, session)
            return team
        return None

    def delete_winning_team(self):
        keys = Cache.get_keys(f"winner_team_key_{self.data['id']}*")
        for key in keys:
            Cache.delete(key)

    async def confirm_round_winner(self, session, team_id):
        async with session.patch(
            f"{self.URL}{self.data['id']}/",
            data={"winner": team_id}, headers={
                    "Authorization": CORE_AUTH_TOKEN
                }
        ) as response:
            m_round = await response.json()
            Round(m_round)
