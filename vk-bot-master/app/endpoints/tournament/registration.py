from aiohttp import ClientResponseError

from app.controller import Response
from app.db import Game, Tournament
from app.endpoint import Endpoint
from app.endpoints.profile import add_game_accounts_endpoint
from app.endpoints.team.teams import teams
from app.endpoints.tournament.tournament import tournament_endpoint


async def update_stage_description(tournament, text, conf=True):
    if tournament.data["educational_type_limit"]:
        edu_limit = tournament.data["educational_type_limit"]
        text += f" - Обучаться в {edu_limit['name']}\n"

    if tournament.data["federal_districts_limit"]:
        federal_limit = tournament.data["federal_districts_limit"]
        text += (f" - Учебное заведение должно находиться в"
                 f" {federal_limit[0]['name']}\n")

    if tournament.data["location_limit"]:
        location_limit = tournament.data["location_limit"]
        text += (f" - Учебное заведение должно находиться в"
                 f" {location_limit[0]['name']}\n")

    if tournament.data["study_team"] and conf:
        text += (f" - Все игроки в команде должны быть из "
                 f"одного учебного заведения")
    return text


async def tournament_registration_handler(state):
    data = state.message.payload_data
    response = Response(state)
    tournament = await Tournament.find_by_id(
        data["id"],
        state.aiohttp_session,
        False,
    )
    confirm_team = await tournament.get_allowed_confirm_teams(
        state.aiohttp_session
    )
    if data["team_id"]:
        try:
            await tournament.register_team(
                state.aiohttp_session, data["team_id"][0]
            )
            return tournament_endpoint
        except ClientResponseError:
            await response.send(
                "Не удалось зарегистрировать вас на этот турнир, "
                "поскольку достигнуто максимальное количество участников!"
            )
            return tournament_endpoint

    game = await Game.find_by_id(
        tournament.data["game"],
        state.aiohttp_session,
    )

    await response.send(
        f"Не получилось найти у вас команду, которую мы бы могли "
        "зарегистрировать на этот турнир.\n"
        "Создайте ее, либо вступите в уже существующую.\n\n"
        "Если вы уже состоите в команде, то попросите вашего капитана "
        "зарегистрировать кoманду на турнир\n\n"
        "Необходимые критерии команды:\n"
        f"- Команды должна быть по игре {game.data['name']}\n"
        "- Команде должна быть рассчитана на "
        f" {tournament.data['allowed_quantity_players_in_team']} игроков"
    )
    if (tournament.data["federal_districts_limit"] or
            tournament.data["location_limit"] or
            tournament.data["educational_type_limit"]):
        text = (
            "Так же обращаем ваше внимание на то что это закрытый турнир, "
            "для того что бы зарегистрироваться на него, капитан команды "
            "должен соответствовать следующим критериям:\n\n"
            " - Именть верифицированный аккаунт\n"
        )

        text = await update_stage_description(tournament, text, False)
        await response.send(text)

    if game.data['platform'] in ('Steam', 'Clash Royale'):
        if tournament.data["allowed_quantity_players_in_team"] == 1:
            text = (
                "\nДля регистрации на этом турнире "
                f"вам необходимо привязать аккаунт {game.data['platform']} "
                "к вашему профилю в боте.\n"
            )
        else:
            text = (
                "И для дальнейшего подтверждения участия на этом турнире "
                f"все члены должны привязать {game.data['platform']} "
                "к профилю в боте.\n"
            )
        await response.send(text)

    return teams


tournament_registration_endpoint = Endpoint(
    name="tournament_registration",
    title="Регистрация",
    description="Вы зарегестрировались!",
    handler=tournament_registration_handler,
    keyboard=None,
)
