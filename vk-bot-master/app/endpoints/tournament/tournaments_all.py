from app.db.models import Tournaments
from app.endpoint import Endpoint
from app.endpoints.tournament.tournaments import tournaments_by_game_endpoint
from app.endpoints.tournament.utils import create_tournaments_keyboard


async def all_tournaments_handler(state):
    data = state.message.payload_data
    tournaments = await Tournaments.all(state.aiohttp_session)
    try:
        tournaments = [
            item
            for item in tournaments.data
            if not item["winner"] and item["game"] == data['game_id']
        ]
    except (TypeError, KeyError):
        return tournaments_by_game_endpoint
    data = state.message.payload_data

    all_tournaments_endpoint.keyboard = await create_tournaments_keyboard(
        tournaments, data, all_tournaments_endpoint.name, data['game_id']
    )


all_tournaments_endpoint = Endpoint(
    name="all_tournaments",
    title="Все турниры",
    description="Вcе турниры платформы",
    handler=all_tournaments_handler,
    keyboard=None,
)
