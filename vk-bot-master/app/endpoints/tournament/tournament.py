from app.db import Team
from app.db.models.core import Tournament
from app.endpoint import Endpoint
from app.endpoints.tournament.utils import (
    create_description_tournaments,
    create_keyboard_tournament
)


async def tournament_handler(state):
    data = state.message.payload_data
    tournament = await Tournament.find_by_id(
        data["id"], state.aiohttp_session,
    )

    description = f"Турнир {tournament.data['name']}\n\n"

    tournament_endpoint.attachment = None
    if "info" in data:
        res = await create_description_tournaments(state, tournament)
        if 'photo' in res:
            tournament_endpoint.attachment = res
        else:
            description += res

    if tournament.data["winner"]:
        team = await Team.find_by_id(
            tournament.data["winner"], state.aiohttp_session
        )
        description += f"\n\nПобедитель: {team.data['name']}"
    tournament_endpoint.description = description

    keyboard = await create_keyboard_tournament(tournament, state)
    tournament_endpoint.keyboard = keyboard


tournament_endpoint = Endpoint(
    name="tournament",
    title="Турнир",
    description="Страница турнира",
    handler=tournament_handler,
    keyboard=None,
    attachment=None
)
