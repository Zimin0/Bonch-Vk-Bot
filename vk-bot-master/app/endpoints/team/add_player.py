from datetime import datetime
from app.controller import Response
from app.db.models import Team
from app.db.models.core.teams import TeamInvites
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.team.team import team_endpoint, team_list
from app.endpoints.team.teams import teams
from app.endpoints.team.utils import verify_invite
from app.endpoints.main import endpoint as main_endpoint


async def add_player_handler(state):
    data = state.message.payload_data
    if not data:
        data = {"id": state.user.get_current_team_id()}

    team = await Team.find_by_id(data["id"], state.aiohttp_session)
    try:
        if team.data["players_count"] <= len(team.data["players"]):
            response = Response(state)
            await response.send(
                "Достигнут лимит по количеству игроков в этой команде,"
                "вы не можете больше никого приглашать"
                )
            return team_list
    except KeyError:
        await Team.find_by_id(data["id"], state.aiohttp_session, False)
        return add_player

    add_player.keyboard = [[BackwardButton("team_list", {"id": data["id"]})]]
    state.user.set_current_team_id(data["id"])
    state.user.set_next_state("team_add_player_confirm")


add_player = Endpoint(
    name="team_add_player",
    title="Добавить игрока",
    description="Введите ссылку на страницу игрока,"
    "\nкоторого хотите пригласить в команду",
    handler=add_player_handler,
    keyboard=None,
)


async def add_player_confirm_handler(state):
    response = Response(state)
    team_id = state.user.get_current_team_id()
    if not team_id:
        await response.send("ОШИБКА!\n"
                            "В работе сервиса произошла какая-то ошибка, "
                            "повторите ваш запрос немного позже")
        return main_endpoint

    team = await Team.find_by_id(team_id, state.aiohttp_session)
    add_player_confirm.keyboard = [
        [BackwardButton("team_add_player", {"id": team_id})]
    ]
    try:
        response_msg = await verify_invite(state, team)
    except (KeyError, IndexError):
        await Team.find_by_id(team_id, state.aiohttp_session, False)
        await response.send("ОШИБКА!\n"
                            "В работе сервиса произошла какая-то ошибка, "
                            "повторите ваш запрос")
        return add_player
    await response.send(response_msg)
    return add_player


add_player_confirm = Endpoint(
    name="team_add_player_confirm",
    title="null",
    description="qwe",
    handler=add_player_confirm_handler,
    keyboard=None,
)


async def add_player_invite_handler(state):
    response = Response(state)
    data = state.message.payload_data
    invite = await TeamInvites.find_by_id(
        data["invite_id"],
        state.aiohttp_session
    )
    invite = invite.data
    if not invite['expired']:
        await response.send("Срок приглашения истек! "
                            "Оно больше не действительно")
        return teams
    if invite['type'] == 2:
        await response.send("Приглашение не действительно!")
        return teams

    add_player_invite_endpoint.description = (
        f"Вас пригласили в команду {invite['team_name']}"
    )
    add_player_invite_endpoint.keyboard = [
        [
            Button(
                "team_add_player_invite_accept",
                "Принять",
                {"id": data["invite_id"], "accept": True},
            ),
            Button(
                "team_add_player_invite_accept",
                "Отклонить",
                {"id": data["invite_id"], "accept": False},
            ),
        ]
    ]


add_player_invite_endpoint = Endpoint(
    name="team_add_player_invite",
    title="null",
    description="qwe",
    handler=add_player_invite_handler,
    keyboard=None,
)


async def team_add_player_invite_accept_handler(state):
    response = Response(state)
    data = state.message.payload_data
    invite = await TeamInvites.find_by_id(data["id"], state.aiohttp_session)
    await invite.set_checked(state.aiohttp_session)
    if data["accept"]:
        team = await Team.find_by_id(
            invite.data["team"],
            state.aiohttp_session,
            False
        )
        if team.data["players_count"] <= len(team.data["players"]):
            await response.send(
                "Достигнут лимит по количеству игроков в этой команде,"
                "вы не можете вступить в нее"
            )
            return teams
        if team.data['allow_chang']:
            await team.add_player(state.aiohttp_session, state.user.id)
            state.message.payload_data["id"] = invite.data["team"]
            return team_endpoint
        else:
            await response.send("Команда сейчас участвует в турнире, "
                                "измененеи состава заблокированно!")
    return teams


team_add_player_invite_accept_endpoint = Endpoint(
    name="team_add_player_invite_accept",
    title="null",
    description="qwe",
    handler=team_add_player_invite_accept_handler,
    keyboard=None,
)
