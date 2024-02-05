from app.db.models.core import Match, Round
from app.endpoint import BackwardButton, Button, Endpoint


async def tournament_round_handler(state):
    data = state.message.payload_data
    session = state.aiohttp_session
    tournament_round = await Round.find_by_id(data["round_id"], session)
    match = await Match.find_by_id(data["match_id"], session)

    tournament_round_endpoint.description = (
        f"Раунд {tournament_round.data['number']} из "
        f"{match.data['quantity_wins'] + 1} "
    )
    tournament_round_endpoint.keyboard = [
        [
            Button(
                "tournament_round_winner",
                "Ввести результаты раунда",
                data,
            )
        ],
        [
            BackwardButton(
                "tournament_happening",
                data,
            )
        ],
    ]


tournament_round_endpoint = Endpoint(
    name="tournament_round",
    title="Текущий матч",
    description="матч",
    handler=tournament_round_handler,
    keyboard=None,
)
