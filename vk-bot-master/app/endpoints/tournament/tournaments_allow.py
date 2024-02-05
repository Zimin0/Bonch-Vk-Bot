from app.db.models.core.tournaments import AllowTournaments
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.tournament.utils import create_tournaments_keyboard
from app.endpoints.tournament.tournaments import tournaments_by_game_endpoint


async def allow_tournaments_handler(state):
    data = state.message.payload_data
    user = state.user.data
    tournaments = await AllowTournaments.get_allow_tournaments(
        state.aiohttp_session, user["id"]
    )
    try:
        tournaments = [
            item
            for item in tournaments.data
            if not item["winner"] and item["game"] == data['game_id']
        ]
    except (TypeError, KeyError):
        return tournaments_by_game_endpoint

    data = state.message.payload_data
    description = "Все доступные вам турниры"
    if not tournaments:
        description = ("Сейчас на платформе нету доступных для вас турниров.\n"
                       "Возможно вы не состоите ни в одной команде.\n\n"
                       'Создать команду можно в "Профиль" > "Мои команды"\n\n'
                       "Посмотреть по каким играм сейчас проходят турниры "
                       'можно в "Турниры" > "Все турниры"\n\n'
                       "И еще больше турниров доступно для "
                       "верифицированных учетных записей!")
        allow_tournaments_endpoint.keyboard = [
            [
                Button("all_tournaments", "Все турниры"),
                Button(
                    "teams_by_game", "Мои команды", {
                        "n": "u"
                    }
                    ),
            ],
            [BackwardButton("tournaments")],
        ]
    else:
        allow_tournaments_endpoint.keyboard = await create_tournaments_keyboard(
            tournaments, data, allow_tournaments_endpoint.name, data['game_id']
        )
    allow_tournaments_endpoint.description = description


allow_tournaments_endpoint = Endpoint(
    name="allow_tournaments",
    title="Доступные турниры",
    description="Все доступные вам турниры",
    handler=allow_tournaments_handler,
    keyboard=[[BackwardButton("tournaments")]],
)
