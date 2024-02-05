from vk_api.keyboard import VkKeyboardColor

from app.db.models.core.games import Games
from app.db.models.core.user import User
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.utils import chunks_generators

user_status = {
    False: "не подтвержден",
    True: "подтвержден"
}


async def handler(state):
    user = state.user
    data = state.message.payload_data
    if data:
        if 'send' in data:
            if data['send']:
                if data['game'] not in user.data['game_subscription']:
                    user.data['game_subscription'].append(data['game'])
            else:
                if data['game'] in user.data['game_subscription']:
                    user.data['game_subscription'].remove(data['game'])
            await user.update_game_subscription(state.aiohttp_session)

    all_games = await Games.all(state.aiohttp_session)
    all_games = {game['id']: game['name'] for game in all_games.data}
    keyboard = []
    for game in all_games:
        if game in user.data['game_subscription']:
            keyboard.append(
                Button(
                    "notification_settings",
                    all_games[game],
                    {
                        "send": False,
                        "game": game
                    },
                    VkKeyboardColor.POSITIVE
                )
            )
        else:
            keyboard.append(
                Button(
                    "notification_settings",
                    all_games[game],
                    {
                        "send": True,
                        "game": game
                    },
                )
            )

    keyboard = list(chunks_generators(keyboard, 2))

    if user.data['registration_sate'] > 3:
        keyboard += [[BackwardButton("profile")]]

    endpoint.keyboard = keyboard
    description = ("Тут вы можете настроить уведомления, "
                   "которые будут вам приходить:\n")
    for game in all_games:
        if game in user.data['game_subscription']:
            description += f"\n{all_games[game]} - включены ✅"
        else:
            description += f"\n{all_games[game]} - выключены 🚫"

    endpoint.description = description

endpoint = Endpoint(
    name="notification_settings",
    title="Настройки уведомлений",
    description="",
    handler=handler,
    keyboard=[],
)
