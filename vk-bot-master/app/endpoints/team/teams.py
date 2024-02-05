from app.db import Games
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.utils import chunks_generators


async def teams_handler(state):
    state.user.delete_all_user_cache()
    data = state.message.payload_data
    user_teams = await state.user.get_visible_teams(state.aiohttp_session)

    try:
        description = (
            f"Вот ваши команды по игре {data['game_name']}:\n"
        )
        for team in user_teams:
            if team.data['game'] == data['game_id']:
                description += (f"Предусмотренно игроков: "
                                f"{team.data['players_count']} — "
                                f"{team.data['name']}\n"
                                )
    except (KeyError, TypeError):
        return teams_by_game

    keyboard = list(
        chunks_generators(
            [
                Button(
                    "team",
                    f"{item.data['name']}",
                    {
                        "id": item.data["id"]
                    }
                )
                for item in user_teams
                if item.data['game'] == data['game_id']
            ],
            2,
        )
    )
    if data['show_c_b']:
        keyboard += [
            [Button("create_team_select_game", "Создать команду")],
            [BackwardButton("profile")],
        ]
    else:
        keyboard += [
            [BackwardButton("teams_by_game")],
        ]

    teams.keyboard = keyboard
    teams.description = description


teams = Endpoint(
    name="teams",
    title="Мои команды",
    description="Выбери команду или создай новую!",
    handler=teams_handler,
    keyboard=None,
)


async def teams_by_game_handler(state):
    state.user.delete_all_user_cache()
    data = state.message.payload_data
    user_teams = await state.user.get_visible_teams(state.aiohttp_session)
    user_games = [team.data['game'] for team in user_teams]
    games = await Games.all(state.aiohttp_session)
    games_name = {game['id']: game['name'] for game in games.data}

    if len(set(user_games)) == 1:
        data["game_id"] = user_games[0]
        data["game_name"] = games_name[user_games[0]]
        data["show_c_b"] = True
        return teams

    description = (
        f"По какой игре вы хотите увидить команды?"
    )
    if not user_games:
        description = (
            f"Вы еще не состоите ни в одной команде, но вы можете создать свою!"
        )

    keyboard = list(
        chunks_generators(
            [
                Button(
                    "teams",
                    games_name[item],
                    {
                        "game_id"  : item,
                        "game_name": games_name[item],
                        "show_c_b" : False,
                    }
                )
                for item in set(user_games)
            ],
            2,
        )
    )
    keyboard += [
        [Button("create_team_select_game", "Создать команду")],
        [BackwardButton("profile")],
    ]

    teams_by_game.keyboard = keyboard
    teams_by_game.description = description


teams_by_game = Endpoint(
    name="teams_by_game",
    title="Мои команды",
    description="Выбери команду или создай новую!",
    handler=teams_by_game_handler,
    keyboard=None,
)
