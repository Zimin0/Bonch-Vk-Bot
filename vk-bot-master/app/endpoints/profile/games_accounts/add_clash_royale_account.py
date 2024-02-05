from app.controller import Response
from app.db import Platforms
from app.endpoint import BackwardButton, Endpoint
from app.endpoints.profile.games_accounts.add_game_accounts import \
    add_game_accounts_endpoint


async def add_handler(state):
    user_accounts = await state.user.get_game_accounts(state.aiohttp_session)

    platforms = await Platforms.all(state.aiohttp_session)
    clash_royale_platform_id = [
        platform["id"]
        for platform in platforms.data
        if platform["name"] == "Clash Royale"
    ]

    clash_royale_account = None
    for account in user_accounts:
        if account["platform"] == clash_royale_platform_id[0]:
            clash_royale_account = account
    if clash_royale_account:
        description = (
            f"Вы привязали аккаунт Clash Royale:\n\n"
            f"{clash_royale_account['nick_name']}\n\n"
            f"Теперь вы можете участвовать в турнирах по этой игре!\n\n"
            f"Если хотите привязать другой аккаунт, то "
            f"обратитесь к администраторам сообщества!"
        )
    else:
        description = (
            "Введи свой игровой тег.\n\n"
            "Его можно найти в профиле игрока,"
            " прямо под твоим никнеймом.\n\n"
            "Начинается он с - #\n"
        )
        state.user.set_next_state("clash_royale_account_confirmation")
    add_clash_royale_account_endpoint.description = description


add_clash_royale_account_endpoint = Endpoint(
    name="add_clash_royale_account",
    title="Привязать аккаунт",
    description="Добро пожаловать в твой профиль!",
    handler=add_handler,
    keyboard=[[BackwardButton("add_game_accounts")]],
)


async def confirmation_handler(state):
    response = Response(state)
    platforms = await Platforms.all(state.aiohttp_session)
    clash_royale_platform_id = [
        platform["id"]
        for platform in platforms.data
        if platform["name"] == "Clash Royale"
    ]
    if not clash_royale_platform_id:
        await response.send(
            "В данный момент привязать свой аккаунт нельзя, "
            "попробуйте еще раз позже"
        )

    data = {
        "platform": clash_royale_platform_id[0],
        "platform_token": state.message.text,
        "user": state.user.id,
    }
    res = await state.user.create_game_account(state.aiohttp_session, data)
    if "error" in res:
        await response.send(
            "Не удалось привязать аккаунт,"
            " проверьте правильность введенного тега!"
        )
        return add_clash_royale_account_endpoint

    return add_game_accounts_endpoint


clash_royale_account_confirmation_endpoint = Endpoint(
    name="clash_royale_account_confirmation",
    title="Привязать аккаунт",
    description="Добро пожаловать в твой профиль!",
    handler=confirmation_handler,
    keyboard=[[BackwardButton("add_clash_royale_account")]],
)
