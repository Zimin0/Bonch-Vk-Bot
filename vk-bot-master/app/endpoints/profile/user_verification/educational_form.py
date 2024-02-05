from app.controller import Response
from app.db.models.core.educationals import (EducationalInstitution,
                                             EducationalLocation,
                                             EducationalType,
                                             UserVerificationRequest)
from app.endpoint import BackwardButton, Button, Endpoint
from app.endpoints.profile import profile_endpoint
from app.endpoints.profile.user_verification.utils import \
    create_edu_location_keyboard
from app.endpoints.profile.user_verification.main_modal import \
    endpoint as main_verification_endpoint
from app.endpoints.utils import chunks_generators


async def edu_type_handler(state):
    edu_type = await EducationalType.all(state.aiohttp_session)
    keyboard = list(
        chunks_generators(
            [
                Button(
                    "user_verif_edu_location",
                    item["name"],
                    {"edu_type_id": item["id"], "page": 0},
                )
                for item in edu_type.data
            ],
            2,
        )
    )
    keyboard += [
        [BackwardButton("user_verification")],
    ]
    edu_type_endpoint.keyboard = keyboard


edu_type_endpoint = Endpoint(
    name="user_verif_edu_type",
    title="Тип учебного заведения",
    description="Укажите тип вашего учебного заведения",
    handler=edu_type_handler,
    keyboard=None,
)


async def edu_location_handler(state):
    page = 0
    data = state.message.payload_data
    if 'page' in data:
        page = data['page']
    edu_location = await EducationalLocation.all(state.aiohttp_session)
    keyboard = await create_edu_location_keyboard(
        edu_location, data["edu_type_id"], page
    )
    edu_location_endpoint.keyboard = keyboard


edu_location_endpoint = Endpoint(
    name="user_verif_edu_location",
    title="Регион учебного заведения",
    description="Регион учебного заведения",
    handler=edu_location_handler,
    keyboard=[
        [BackwardButton("user_verif_edu_type")],
    ],
)


async def edu_confirm_name_handler(state):
    response = Response(state)
    user = state.user
    data = state.message.payload_data
    if not data:
        return main_verification_endpoint

    edu_institution = await EducationalInstitution.create(
        state.aiohttp_session,
        {"location": data['edu_location_id'], "type": data['edu_type_id']},
    )

    try:
        vk_chat_url = await UserVerificationRequest.create_chat(
            state.aiohttp_session
        )
    except KeyError:
        await response.send(
            "К сожаления сейчас мы не можем зарегистрировать вашу заявку, "
            "повторите ваш запрос немного позднее"
        )
        return main_verification_endpoint

    await UserVerificationRequest.create(
        state.aiohttp_session,
        {"vk_chat_link": vk_chat_url, "user": user.data["id"]},
    )
    await user.update_edu(state.aiohttp_session, edu_institution.data["id"])
    await response.send(
        "Заявка отправленна!\n"
        f"Переходите в беседу {vk_chat_url}, там с вами "
        f"свяжется модератор, c 10:00 до 22:00 ежедневно, "
        f"для того что бы подтвердить введенные вами данные.\n"
    )
    return profile_endpoint


edu_confirm_name_endpoint = Endpoint(
    name="user_verif_edu_confirm_name",
    title=".",
    description="Заявка отправленна",
    handler=edu_confirm_name_handler,
    keyboard=[[BackwardButton("user_verification")]],
)
