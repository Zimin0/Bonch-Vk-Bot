from aiohttp import ClientResponseError

from app.controller import Response
from app.db import Game, Team
from app.db.models import Games, Teams
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.team.teams import teams
from app.endpoints.utils import chunks_generators

from app.endpoints.profile import profile_endpoint


async def create_team_select_game_handler(state):
    games = await Games.all(state.aiohttp_session)
    keyboard = list(
        chunks_generators(
            [
                Button(
                    "create_team_select_player_count",
                    item["name"],
                    {
                        "id": item["id"]
                    }
                )
                for item in games.data
                if (len(item["players_count"]) > 1) or
                   (
                           (len(item["players_count"]) == 1) and
                           (item["players_count"][0] != 1)
                   )
            ],
            2,
        )
    )
    keyboard += [
        [BackwardButton("teams_by_game")],
    ]
    create_team_select_game.keyboard = keyboard


create_team_select_game = Endpoint(
    name="create_team_select_game",
    title="Создать команду",
    description="Выбери игру!",
    handler=create_team_select_game_handler,
    keyboard=[[BackwardButton("profile")]],
)


async def create_team_select_player_count_handler(state):
    data = state.message.payload_data
    try:
        game = await Game.find_by_id(data['id'], state.aiohttp_session)
    except TypeError:
        return create_team_select_game

    keyboard = list(
        chunks_generators(
            [
                Button(
                    "create_team_enter_name",
                    count,
                    {
                        "id": data['id'],
                        "player_count": count
                    }
                )
                for count in game.data['players_count']
                if count != 1
            ],
            2,
        )
    )
    keyboard += [
        [BackwardButton("create_team_select_game")],
    ]
    create_team_select_player_count.keyboard = keyboard


create_team_select_player_count = Endpoint(
    name="create_team_select_player_count",
    title="Создать команду",
    description="Какое количество игроков будет в команде?",
    handler=create_team_select_player_count_handler,
    keyboard=[[BackwardButton("profile")]],
)


async def create_team_enter_name_handler(state):
    response = Response(state)
    data = state.message.payload_data
    if not data:
        data = {
            'id': state.user.get_current_game_id(),
            'player_count': state.user.get_current_player_count()
        }
    user = state.user
    user_teams = await user.get_visible_teams(state.aiohttp_session)
    for team in user_teams:
        if team.data["game"] == data["id"] and \
                team.data["players_count"] == data["player_count"]:
            game = await Game.find_by_id(
                data["id"], state.aiohttp_session
            )
            await response.send(
                f"Вы уже состоите в команде по {game.data['name']} "
                "с эти количеством игроков.\n\n"
                f"Что бы созадть команду с этими параметрами"
                f" вы должны покинуть команду: {team.data['name']}"
            )
            return teams
    state.user.set_next_state("create_team_confirm_name")
    if data:
        state.user.set_current_game_id(data["id"])
        state.user.set_current_player_count(data["player_count"])


create_team_enter_name = Endpoint(
    name="create_team_enter_name",
    title="Создать команду",
    description="Введите название команды!",
    handler=create_team_enter_name_handler,
    keyboard=[[BackwardButton("create_team_select_game")]],
)


async def create_team_confirm_name_handler(state):
    game_id = state.user.get_current_game_id()
    player_count = state.user.get_current_player_count()
    response = Response(state)
    team_name = state.message.text

    if (
            3 > len(team_name)
            or 15 < len(team_name)
            or set("!»№;%:?*()_+=,") & set(team_name)
    ):
        await response.send(
            "Название команды должно быть:\n"
            " - от 3 до 15 символов\n"
            " - без использование символов: !»№;%:?*()_+=,"
        )
        return create_team_enter_name
    try:
        await Team.create(
            state.aiohttp_session,
            {
                "name": team_name,
                "game": game_id,
                "captain": state.user.data["id"],
                "players_count": player_count,
            },
        )

    except ClientResponseError:
        await response.send(
                "Команда с таким названием уже существует!"
            )
        return create_team_enter_name

    await response.send("Команда создана!")
    state.user.delete_current_game_id()
    state.user.delete_current_player_count()
    return profile_endpoint


create_team_confirm_name = Endpoint(
    name="create_team_confirm_name",
    title="Создать команду",
    description="Cgfcb,j!",
    handler=create_team_confirm_name_handler,
    keyboard=[[BackwardButton("create_team_enter_name")]],
)
