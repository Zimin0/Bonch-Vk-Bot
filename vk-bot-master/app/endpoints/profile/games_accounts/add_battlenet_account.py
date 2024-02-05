from app.db import Platforms
from app.endpoint import BackwardButton, Endpoint
from app.settings import CORE_URL


async def add_handler(state):
    user = state.user
    platforms = await Platforms.all(state.aiohttp_session)
    battlenet_id = [
        platform["id"]
        for platform in platforms.data
        if platform["name"] == "Battle.net"
    ]
    user_accounts = await user.get_game_accounts(state.aiohttp_session)
    battlenet_acc = None
    for account in user_accounts:
        if account["platform"] == battlenet_id[0]:
            battlenet_acc = account
    if battlenet_acc:
        description = (
            f"Вы уже привязали аккаунт Battle-net:\n\n"
            f"{battlenet_acc['nick_name']}\n\n"
            f"Теперь вы можете участвовать в турнирах "
            f"по играм этой платформы!\n\n"
            f"Если хотите привязать другой аккаунт, то "
            f"обратитесь к администраторам сообщества!"
        )
    else:
        link = CORE_URL + f"/battlenet/auth/?id={user.data['id']}"
        description = "Для того что бы привязать ваш аккаунт, " \
                      "перейдите по ссылке ниже и " \
                      "авторизайтесь в Battle-net\n\n" \
                      "Это ваша индивидуальная ссылка:\n" \
                      f"{link}"
    add_battlenet_account_endpoint.description = description


add_battlenet_account_endpoint = Endpoint(
    name="add_battlenet_account",
    title="Battle-net",
    description="Добро пожаловать в твой профиль!",
    handler=add_handler,
    keyboard=[[BackwardButton("add_game_accounts")]],
)