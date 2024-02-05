from app.endpoint import BackwardButton, Button, Endpoint


async def handler(state):
    add_game_accounts_endpoint.description = (
        f"{state.user.data['first_name']},"
        f" аккаунт какой платформы вы хотите привязать?"
    )
    keyboard =[
        [
            Button("add_clash_royale_account", "Clash Royale"),
            Button("add_steam_account", "Steam"),
        ],
        [
            Button("add_battlenet_account", "Battle-net"),]
    ]

    if state.user.data['registration_sate'] > 3:
        keyboard += [[BackwardButton("profile")]]

    add_game_accounts_endpoint.keyboard = keyboard

add_game_accounts_endpoint = Endpoint(
    name="add_game_accounts",
    title="Привязать аккаунт",
    description="",
    handler=handler,
    keyboard=None,
)
