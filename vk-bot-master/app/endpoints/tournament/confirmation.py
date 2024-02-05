from app.controller import Response
from app.db import Game, Tournament
from app.endpoint import Endpoint
from app.endpoints.tournament.registration import update_stage_description
from app.endpoints.tournament.tournament import tournament_endpoint


async def tournament_confirmation_handler(state):
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
    confirm_team_ids = [team.data['id'] for team in confirm_team]
    if data["team_id"]:
        if data["team_id"] in confirm_team_ids:
            await tournament.confirm_team(
                state.aiohttp_session, data["team_id"]
            )
            await response.send("Секундочку, сейчас все проверим...")
        else:
            await response.send("Вы НЕ подтвердили свое участие в турнире!")
            game = await Game.find_by_id(
                tournament.data["game"],
                state.aiohttp_session,
            )
            if (tournament.data["federal_districts_limit"] or
                    tournament.data["location_limit"] or
                    tournament.data["educational_type_limit"]):
                text = (
                    "Это закрытый турнир, "
                    "для того что бы подтвердить свое участие в нем, все члены"
                    " команды должны соответствовать следующим критериям:\n\n"
                    " - Именть верифицированный аккаунт\n"
                )
                text = await update_stage_description(tournament, text)

                if tournament.data["allowed_quantity_players_in_team"] != 1:
                    text += (
                        f"\nВ команде должно состоять "
                        f"{tournament.data['allowed_quantity_players_in_team']}"
                        f" игроков"
                    )

                if game.data['platform'] in ('Steam', 'Clash Royale'):
                    text += (
                        f"И все члены должны привязать "
                        f"{game.data['platform']} к профилю в боте.\n"
                    )
                await response.send(text)
            else:
                text = (
                    f"\nВ команде должно состоять "
                    f"{tournament.data['allowed_quantity_players_in_team']}"
                    f" игроков"
                )
                if game.data['platform'] in ('Steam', 'Clash Royale'):
                    text += (
                        f"\nИ все члены должны привязать "
                        f"{game.data['platform']} к профилю в боте.\n"
                    )
                await response.send(text)

        return tournament_endpoint
    await response.send(
        "Вы НЕ можете подтвердить свое участие в турнире, "
        "поскольку не зарегистрировались на него ранее!"
    )

    return tournament_endpoint


tournament_confirmation_endpoint = Endpoint(
    name="tournament_confirmation",
    title="Подтвердить",
    description="Вы подтвердили свое участие!",
    handler=tournament_confirmation_handler,
    keyboard=None,
)
