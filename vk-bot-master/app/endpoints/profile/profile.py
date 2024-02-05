from app.db.models.core.educationals import EducationalInstitution
from app.endpoint import BackwardButton, Button, Endpoint

user_status = {False: "не подтвержден", True: "подтвержден"}


async def handler(state):
    user = state.user.data
    educational_institution = user["educational_institution"]
    if educational_institution:
        educational_institution = await EducationalInstitution.find_by_id(
            educational_institution, state.aiohttp_session
        )
        edu_name = "не указанно"
        if "institute" in educational_institution.data:
            edu_name = educational_institution.data["institute"]

    else:
        edu_name = (
            '"не указанно"\n'
            "Вы не сможете участвовать в некоторых "
            "турнирах "
        )

    text = (
        f"{user['first_name']}, добро пожаловать в твой профиль!\n\n"
        f"Учебное заведение: "
        f"{edu_name}\n"
        f"Статус пользователя: {user_status[user['verified']]}\n"
    )
    if user["verified"]:
        text = (
            text + f"Аутентификация личности истекает: "
            f"{user['date_next_verification']}"
        )

    endpoint.description = text


endpoint = Endpoint(
    name="profile",
    title="Профиль",
    description="Добро пожаловать в твой профиль!",
    handler=handler,
    keyboard=[
        [
            Button("add_game_accounts", "Привязать аккаунт"),
            Button("teams_by_game", "Мои команды", {"n": "u"}),
        ],
        [
            Button("user_verification", "Верификация личности"),
            Button("notification_settings", "Настройки уведомлений"),
        ],
        [BackwardButton("main")],
    ],
)
