from app.db import Tournament
from app.db.models.core.csgo import Csgo
from app.endpoint import Endpoint
from app.endpoints.tournament.csgo.peak_stage import (
    tournament_csgo_peak_stage_endpoint,
)
from app.endpoints.tournament.tournaments import tournaments_by_game_endpoint
from app.endpoints.tournament.utils import (create_description_match,
                                            create_keyboard_match)


async def tournament_match_csgo_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session
    tournament = await Tournament.find_by_id(data["id"], session)
    tournament.del_grid()

    match = await tournament.get_team_match(session, data["team_id"])
    if not match.data:
        return tournaments_by_game_endpoint

    match_rounds = await match.get_match_rounds(session)

    if match_rounds:
        for match_round in match_rounds:
            print(match_round.data['round_map'])
            if not match_round.data['round_map']:
                return tournament_csgo_peak_stage_endpoint

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
    description = await create_description_match(
        state,
        teams_match,
        match,
        match_rounds,
        tournament.data["number_teams_match"],
    )
    peaks = await Csgo.get_peak_stages(session=session, match_id=match.id)
    peak_text = '\n - '.join(
        [f'{peak["map"]["name"]}'
         for peak in peaks['items']
         if peak['type'] == 'peak']
    )
    description += (f"\nКарты: \n"
                    f" - {peak_text}")
    tournament_match_csgo_endpoint.description = description
    tournament_match_csgo_endpoint.keyboard = keyboard


tournament_match_csgo_endpoint = Endpoint(
    name="tournament_match_csgo",
    title="Текущий матч",
    description="матч",
    handler=tournament_match_csgo_handler,
    keyboard=None,
)
