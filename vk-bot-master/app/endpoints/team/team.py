from app.db.models import Game, Team
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.team.utils import create_team_keyboard


async def team_handler(state):
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    try:
        game = await Game.find_by_id(team.data["game"], state.aiohttp_session)
        team_endpoint.description = (
            f'Команда {team.data["name"]}, по игре {game.data["name"]}\n\n'
            f'Предусмотренное количество игроков - {team.data["players_count"]}'
        )
        team_endpoint.keyboard = [
            [Button(
                "team_list", "Состав команды", {
                    "id": data["id"]
                }
                )],
            [BackwardButton(
                "teams_by_game", {
                    "u": "n"
                }
                )],
        ]
    except KeyError:
        await Team.find_by_id(data["id"], state.aiohttp_session, False)
        return team_endpoint


team_endpoint = Endpoint(
    name="team",
    title="Команда",
    description="",
    handler=team_handler,
    keyboard=None,
)


async def list_handler(state):
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    if "players" not in team.data:
        team = await Team.find_by_id(data["id"], state.aiohttp_session, False)

    team_list.keyboard = await create_team_keyboard(data, state, team)
    players_name = await team.get_string_name_players(state)

    description = f"Состав команды {team.data['name']}:\n" + "\n".join(
        players_name
    )
    description += ("\n\n✔ - верификация аккаунта\n"
                    "⭐ - капитан\n")
    if not team.data["allow_chang"]:
        description += (
            "\n\nКоманда сейчас участвует в турнире, "
            "изменение состава заблокированно!"
            "\n\n(Изменить состав можно будет через "
            "20 минут после того как команда покинет турнир)"
        )

    team_list.description = description


team_list = Endpoint(
    name="team_list",
    title="Состав команды",
    description="",
    handler=list_handler,
    keyboard=None,
)
