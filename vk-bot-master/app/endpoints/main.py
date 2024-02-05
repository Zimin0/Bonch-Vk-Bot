from vk_api.keyboard import VkKeyboardColor

from app.controller import Response
from app.endpoint import Button, Endpoint
from .profile import add_game_accounts_endpoint, \
    user_notification_settings_endpoint, user_verif_endpoint

reg_states = {
    1: user_notification_settings_endpoint,
    2: add_game_accounts_endpoint,
    3: user_verif_endpoint
}

reg_msg = {
    1: '"Настройки уведомлений"',
    2: '"Привязать аккаунт"',
    3: '"Верификация личности"'
}


async def handler(state):
    state.user.delete_all_user_cache()
    user = state.user
    data = state.message.payload_data
    keyboard = [["profile", "tournaments"]]
    description = "Выберете один из пунктов меню"

    if not user.data['vk_id']:
        await user.add_vk_id(state.aiohttp_session, state.message.peer_id)

    if data:
        if 'state' in data:
            user.data['registration_sate'] = data['state'] + 1
            await user.update_data(state.aiohttp_session)
            user.delete_all_user_cache()
            if data['accept']:
                return reg_states[data['state']]
            else:
                response = Response(state)
                await response.send(
                    f"Вы можете настроить это позже в \n"
                    f"\"Профиль\" > {reg_msg[data['state']]}")

    registration_state = user.data['registration_sate']
    if registration_state <= 3:
        if registration_state == 1:
            description = "Хотите настроить уведомления?"
        elif registration_state == 2:
            description = "Хотите привязать игровой аккаунт к профилю?"
        elif registration_state == 3:
            description = "Хотите верифицировать ваш аккаунт?"
        keyboard = [
            [Button(
                "main",
                "Да",
                {"state": registration_state, "accept": True}
            ),
             Button(
                "main",
                "Нет",
                {"state": registration_state, "accept": False},
                 VkKeyboardColor.NEGATIVE
            )]
        ]
    endpoint.keyboard = keyboard
    endpoint.description = description


endpoint = Endpoint(
    name="main",
    title="Главная",
    description="Выберете один из пунктов меню",
    handler=handler,
    keyboard=[["profile", "tournaments_by_game"]],
)
