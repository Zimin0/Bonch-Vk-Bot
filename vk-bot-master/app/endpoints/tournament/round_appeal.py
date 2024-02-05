from app.controller import Response
from app.db.models.core import Match
from app.endpoint import Endpoint
from app.endpoints.tournament import tournament_match_chat_endpoint


async def tournament_round_appeal_handler(state):
    data = state.message.payload_data
    match = await Match.find_by_id(data["match_id"], state.aiohttp_session)
    link = await match.get_or_create_match_chat(state.aiohttp_session)
    text = f"Вызов в матч {match.data['id']}\n{link}"
    await match.invite_referee(state.aiohttp_session, text)
    response = Response(state)
    await response.send("Судья извещен! Скоро он зайдет в беседу матча.")
    return tournament_match_chat_endpoint


tournament_round_appeal_endpoint = Endpoint(
    name="tournament_round_appeal_winner",
    title="Аппеляция",
    description="Судья",
    handler=tournament_round_appeal_handler,
    keyboard=None,
)
