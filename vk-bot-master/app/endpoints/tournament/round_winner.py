from app.controller import Response
from app.db import Team
from app.db.models.core import Match, Round
from app.endpoint import Endpoint
from app.endpoints.tournament.match import tournament_match_endpoint
from app.endpoints.tournament.round import tournament_round_endpoint
from app.endpoints.tournament.utils import (create_description_round_winner,
                                            create_keyboard_round_winner,
                                            send_round_results)


async def tournament_round_winner_handler(state):
    data = state.message.payload_data
    t_round = await Round.find_by_id(data["round_id"], state.aiohttp_session)
    if t_round.data["winner"]:
        response = Response(state)
        await response.send(
            f"Победитель в раунде {t_round.data['number']} уже определен"
        )
        return tournament_match_endpoint
    teams_round = [
        await Team.find_by_id(id_team, state.aiohttp_session)
        for id_team in t_round.data["teams"]
    ]
    round_winner = t_round.get_round_winner_votes()

    tournament_round_winner_endpoint.keyboard = (
        await create_keyboard_round_winner(
            state, round_winner, data, t_round, teams_round
        )
    )
    tournament_round_winner_endpoint.description = (
        await create_description_round_winner(
            state, round_winner, data, t_round
        )
    )


tournament_round_winner_endpoint = Endpoint(
    name="tournament_round_winner",
    title="Текущий матч",
    description="Кто выиграл?",
    handler=tournament_round_winner_handler,
    keyboard=None,
)


async def tournament_round_add_winner_handler(state):
    data = state.message.payload_data
    w_round = await Round.find_by_id(data["round_id"], state.aiohttp_session)
    if w_round.get_round_winner_votes():
        return tournament_round_winner_endpoint
    w_round.set_winning_team(data["team_id"], data["team_winner_id"])
    match = await Match.find_by_id(data["match_id"], state.aiohttp_session)
    teams = await match.get_teams_match(state.aiohttp_session)
    team_ids = [team.data["id"] for team in teams]
    team_ids.remove(data["team_id"])
    for team_id in team_ids:
        await send_round_results(state, team_id)
    return tournament_round_endpoint


tournament_round_add_winner_endpoint = Endpoint(
    name="tournament_round_add_winner",
    title="Текущий матч",
    description="Кто выиграл?",
    handler=tournament_round_add_winner_handler,
    keyboard=None,
)


async def tournament_round_confirm_winner_handler(state):
    data = state.message.payload_data
    w_round = await Round.find_by_id(data["round_id"], state.aiohttp_session)
    await w_round.confirm_round_winner(
        state.aiohttp_session, data["team_winner_id"]
    )
    w_round.delete_winning_team()
    return tournament_match_endpoint


tournament_round_confirm_winner_endpoint = Endpoint(
    name="tournament_round_confirm_winner",
    title="Текущий матч",
    description="Кто выиграл111?",
    handler=tournament_round_confirm_winner_handler,
    keyboard=None,
)
