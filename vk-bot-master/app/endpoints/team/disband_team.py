from app.db.models import Team
from app.endpoint import Endpoint
from app.endpoints.team.teams import teams_by_game


async def disband_handler(state):
    data = state.message.payload_data
    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    await team.disband(state.aiohttp_session)
    return teams_by_game


disband = Endpoint(
    name="team_disband",
    title="Распустить команду",
    description="1",
    handler=disband_handler,
    keyboard=None,
)
