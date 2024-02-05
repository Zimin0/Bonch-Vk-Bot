from app.db import Tournament
from app.db.models.core import Match
from app.endpoint import BackwardButton, Endpoint


async def tournament_match_chat_handler(state):
    data = state.message.payload_data
    match = await Match.find_by_id(data["match_id"], state.aiohttp_session)
    tournament = await Tournament.find_by_id(data["id"], state.aiohttp_session)
    match_teams = await match.get_teams_match(state.aiohttp_session)
    if len(match_teams) == tournament.data["number_teams_match"]:
        link = await match.get_or_create_match_chat(state.aiohttp_session)
        tournament_match_chat_endpoint.description = link
    else:
        tournament_match_chat_endpoint.description = (
            "Ссылка на беседу появится после определения соперника!"
        )
    tournament_match_chat_endpoint.keyboard = [
        [BackwardButton("tournament_happening", data)]
    ]


tournament_match_chat_endpoint = Endpoint(
    name="tournament_match_chat",
    title="Текущий матч",
    description="беседа матча",
    handler=tournament_match_chat_handler,
    keyboard=None,
)
