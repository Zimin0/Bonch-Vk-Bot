from app.endpoint import BackwardButton, Button, Endpoint


async def handler(state):
    user = state.user
    verified = user.data["verified"]
    endpoint.description = (
        "Проходя процедуру аутентификации личности в "
        "нашей системе,"
        "вы получете возможность участвовать в закрытых "
        "турнирах.\n\n"
        "Начав процедуру аутентификации, вы даете "
        "согласие на "
        "обработку ваших персональных данных! "
    )

    verif_request = await user.get_verification_request_from_core(
        state.aiohttp_session
    )
    keyboard = []
    if verif_request:
        vk_chat_url = verif_request.data["vk_chat_link"]
        endpoint.description = (
            "Вы уже отправили заявку!\n"
            f"Переходите в беседу {vk_chat_url}, "
            f"там с вами свяжется модератор,"
            f" для того что бы подтвердить введенные вами данные."
        )
    elif verified:
        endpoint.description = (
            "Вы уже прошли процедуру аутентификации.\n"
            "Она будет действительна до "
            f"{user.data['date_next_verification']}.\n"
            "Для изменения уже подтвержденных данных "
            "обращайтесь к администраторам сообщества!"
        )
    else:
        keyboard = [
            [
                Button("user_verif_edu_type", "Начать аутентификацию"),
            ]
        ]

    if user.data['registration_sate'] > 3:
        keyboard += [[BackwardButton("profile")]]

    endpoint.keyboard = keyboard


endpoint = Endpoint(
    name="user_verification",
    title="Верификация личности",
    description="123",
    handler=handler,
    keyboard=[],
)
