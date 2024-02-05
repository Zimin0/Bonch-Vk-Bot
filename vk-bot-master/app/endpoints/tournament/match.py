from app.db import Games, Tournament
from app.endpoint import Endpoint
from app.endpoints.tournament.csgo.match import tournament_match_csgo_endpoint
from app.endpoints.tournament.tournaments import tournaments_by_game_endpoint
from app.endpoints.tournament.utils import (create_description_match,
                                            create_keyboard_match
                                            )


async def tournament_match_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session
    tournament = await Tournament.find_by_id(data["id"], session)

    if await tournament.is_csgo(session):
        return tournament_match_csgo_endpoint
    tournament.del_grid()
    match = await tournament.get_team_match(session, data["team_id"])
    if not match.data:
        return tournaments_by_game_endpoint

    match_rounds = await match.get_match_rounds(session)
    teams_match = await match.get_teams_match(session)
    user = state.user.data
    is_captain = False
    for team in teams_match:
        if user['id'] == team.data['captain']:
            is_captain = True

    keyboard = await create_keyboard_match(
        match_rounds,
        match,
        data,
        teams_match,
        tournament.data["number_teams_match"],
        is_captain
    )
    tournament_match_endpoint.description = await create_description_match(
        state,
        teams_match,
        match,
        match_rounds,
        tournament.data["number_teams_match"],
    )
    tournament_match_endpoint.keyboard = keyboard


tournament_match_endpoint = Endpoint(
    name="tournament_happening",
    title="Текущий матч",
    description="матч",
    handler=tournament_match_handler,
    keyboard=None,
)
