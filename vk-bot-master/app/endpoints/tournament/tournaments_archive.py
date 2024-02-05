from app.db.models import Tournaments
from app.endpoint import BackwardButton, Endpoint
from app.endpoints.tournament.utils import create_tournaments_keyboard
from app.endpoints.tournament.tournaments import tournaments_by_game_endpoint


async def archive_tournaments_handler(state):
    data = state.message.payload_data
    tournaments = await Tournaments.all(state.aiohttp_session)
    try:
        tournaments = [
            item
            for item in tournaments.data
            if item["winner"] and item["game"] == data['game_id']
        ]
    except (TypeError, KeyError):
        return tournaments_by_game_endpoint

    data = state.message.payload_data

    archive_tournaments_endpoint.keyboard = await create_tournaments_keyboard(
        tournaments, data, archive_tournaments_endpoint.name, data['game_id']
    )


archive_tournaments_endpoint = Endpoint(
    name="archive_tournaments",
    title="Архивные турниры",
    description="Архив турниров нашей платформы",
    handler=archive_tournaments_handler,
    keyboard=[[BackwardButton("tournaments")]],
)
