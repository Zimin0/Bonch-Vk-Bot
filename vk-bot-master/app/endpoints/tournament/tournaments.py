from app.db import Games, Tournaments
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.utils import chunks_generators


async def tournaments_handler(state):
    data = state.message.payload_data
    try:
        description = (
            f"Какие турниры по игре {data['game_name']} вы хотите посмотреть?"
        )
    except (KeyError, TypeError):
        return tournaments_by_game_endpoint
    tournaments_endpoint.description = description
    tournaments_endpoint.keyboard = [
        [Button("all_tournaments", "Все турниры", data),
         Button("allow_tournaments", "Доступные турниры", data)],
        [Button("archive_tournaments", "Архивные турниры", data)],
        [BackwardButton("tournaments_by_game")]
    ]


tournaments_endpoint = Endpoint(
    name="tournaments",
    title="Турниры",
    description="Турниры нашей платформы",
    handler=tournaments_handler,
    keyboard=[
        ["all_tournaments", "allow_tournaments"],
        ["archive_tournaments"],
    ],
)


async def tournaments_by_game_handler(state):
    games = await Games.all(state.aiohttp_session)
    games_name = {game['id']: game['name'] for game in games.data}

    tournaments = await Tournaments.all(state.aiohttp_session)
    tournament_games = [
        tournament['game']
        for tournament in tournaments.data
        if not tournament['archived']
    ]
    description = (
        f"По какой игре вы хотите увидить турниры?"
    )
    keyboard = list(
        chunks_generators(
            [
                Button(
                    "tournaments",
                    games_name[item],
                    {
                        "game_id": item,
                        "game_name": games_name[item]
                    }
                )
                for item in set(tournament_games)
            ],
            2,
        )
    )
    keyboard += [
        [BackwardButton("main")],
    ]

    tournaments_by_game_endpoint.keyboard = keyboard
    tournaments_by_game_endpoint.description = description


tournaments_by_game_endpoint = Endpoint(
    name="tournaments_by_game",
    title="Турниры",
    description="Турниры нашей платформы",
    handler=tournaments_by_game_handler,
    keyboard=[
        ["all_tournaments", "allow_tournaments"],
        ["archive_tournaments"],
    ],
)
