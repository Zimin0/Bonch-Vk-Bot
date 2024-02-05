from app.controller import Response
from app.db.models import Team
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.team import teams
from app.endpoints.utils import chunks_generators


async def kick_player_handler(state):
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    players = await team.get_players(state.aiohttp_session, False)
    keyboard = list(
        chunks_generators(
            [
                Button(
                    "team_kick_player_confirm",
                    f"{item.data['first_name']} {item.data['last_name']}",
                    {"id_player": item.data["id"], "id": data["id"]},
                )
                for item in players
            ],
            2,
        )
    )
    keyboard += [[BackwardButton("team_list", {"id": data["id"]})]]
    kick_player.keyboard = keyboard
    if len(players) < 1:
        kick_player.description = "Ты один в команде, некого исключать..."
    else:
        kick_player.description = "Кого вы хотите исключить?"


kick_player = Endpoint(
    name="team_kick_player",
    title="Исключить игрока",
    description="",
    handler=kick_player_handler,
    keyboard=None,
)


async def kick_player_confirm_handler(state):
    response = Response(state)
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    await team.kick_player(state.aiohttp_session, data["id_player"])
    if data["id_player"] == state.user.id:
        kick_player_confirm.description = "Выполнено!"
        return teams
    return kick_player


kick_player_confirm = Endpoint(
    name="team_kick_player_confirm",
    title="Готово",
    description="Он исключен!",
    handler=kick_player_confirm_handler,
    keyboard=None,
)
