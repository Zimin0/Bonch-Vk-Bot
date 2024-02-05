import re
from pprint import pprint

from app.db.models import LocalUser, User
from app.db.models.core.teams import TeamInvites
from app.endpoint import BackwardButton, Button
from app.endpoints.utils import chunks_generators
from app.vk import get_vk_user_by_id


# async def send_invite(state, user_id, team_id):
#     user = await User.find_by_id(user_id, state.aiohttp_session)
#     data = {
#         "text": "Вам пришло приглашение в команду",
#         "endpoints": [
#             {
#                 "name": "team_add_player_invite",
#                 "title": "Посмотреть",
#                 "payload": {"team_id": team_id},
#             }
#         ],
#     }
#     await user.send_notification(state.aiohttp_session, data)


async def get_screen_name(text):
    if "/" in text:
        text = re.search(r"(?<=vk.com/)[a-z0-9._-]+", text)
        if text:
            return text.group(0)
    if "@" in text:
        text = re.search(r"(id[-+]?\d+)", text)
        if text:
            return text.group(0)
    return None


async def verify_invite(state, team):
    user_msg = state.message.text
    screen_name = await get_screen_name(user_msg)
    if not screen_name:
        return "Вы ввели неверную ссылку\n\n"

    id_add_user = await get_vk_user_by_id(state.aiohttp_session, screen_name)
    if not id_add_user:
        return (
            "Вы ввели неверную ссылку, "
            "такого пользователя вк не существует."
        )

    user = await LocalUser.find_by_vk_id(state, int(id_add_user["id"]))
    if not user:
        return (
            "Этот пользователь еще не пользовался ботом, "
            "в не можете его пригласить"
        )

    if user.core_id in team.data["players"]:
        return "Он уже есть в команде\n\n"

    data = {
        "team": team.data["id"],
        "user": user.core_id,
    }
    await TeamInvites.create(state.aiohttp_session, data=data)

    return "Приглашение отправлено!\n\n"


team_keyboard_names = (
    ("team_disband", "Распустить команду"),
    ("team_add_player", "Добавить игрока"),
    ("team_kick_player", "Исключить игрока"),
    ("team_new_captain", "Назначить капитана"),
)


async def create_team_keyboard(data, state, team):
    captain = await team.get_captain(state.aiohttp_session)
    keyboard = []
    if captain.data["id"] == state.user.id:
        if team.data["allow_chang"]:
            for button in team_keyboard_names:
                keyboard.append(
                    Button(button[0], button[1], {"id": data["id"]})
                )
        else:
            for button in team_keyboard_names:
                keyboard.append(
                    Button("team_list", button[1], {"id": data["id"]})
                )
        keyboard = list(chunks_generators(keyboard, 2))
    else:
        if team.data["allow_chang"]:
            keyboard += [
                [
                    Button(
                        "team_kick_player_confirm",
                        f"Покинуть команду",
                        {"id_player": state.user.id, "id": data["id"]},
                    )
                ]
            ]
        else:
            keyboard += [
                [
                    Button(
                        "team_list",
                        f"Покинуть команду",
                        {"id_player": state.user.id, "id": data["id"]},
                    )
                ]
            ]

    keyboard += [[BackwardButton("team", {"id": data["id"]})]]
    return keyboard
