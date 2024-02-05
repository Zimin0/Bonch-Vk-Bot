from app.controller import Response
from app.db.models import Team
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.team.team import team_list
from app.endpoints.utils import chunks_generators


async def new_captain_handler(state):
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    players = await team.get_players(state.aiohttp_session, False)
    players_buttons = [
        Button(
            "team_new_captain_confirm",
            f"{item.data['first_name']} {item.data['last_name']}",
            {"id_player": item.data["id"], "id": data["id"]},
        )
        for item in players
    ]
    keyboard = list(chunks_generators(players_buttons, 2))
    keyboard += [[BackwardButton("team_list", {"id": data["id"]})]]
    new_captain.keyboard = keyboard
    if len(players) < 1:
        new_captain.description = "Ты один в команде, некого назначать 😞"
    else:
        new_captain.description = "Кого вы хотите назначить новым капитаном?"


new_captain = Endpoint(
    name="team_new_captain",
    title="Исключить игрока",
    description="",
    handler=new_captain_handler,
    keyboard=None,
)


async def new_captain_confirm_handler(state):
    response = Response(state)
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    await team.new_captain(state.aiohttp_session, data["id_player"])
    await response.send(new_captain_confirm.description)
    return team_list


new_captain_confirm = Endpoint(
    name="team_new_captain_confirm",
    title="Готово",
    description="Да здравствует новый Капитан!",
    handler=new_captain_confirm_handler,
    keyboard=None,
)
