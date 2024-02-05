import random
from io import BytesIO

from aiohttp import FormData

from app.db.utils import client_exception_wrapper
from app.settings import VK_TOKEN

URL = "https://api.vk.com/method/"
DEFAULT_DATA = {
    "access_token": VK_TOKEN,
    "v": "5.131",
}


@client_exception_wrapper
async def send_message(session, data):
    if not data["keyboard"]:
        del data["keyboard"]
    await session.post(
        f"{URL}messages.send",
        ssl=True,
        data={
            **data,
            **DEFAULT_DATA,
            "random_id": random.randint(-2147483648, +2147483648),
        },
    )


@client_exception_wrapper
async def get_vk_user_by_id(session, vk_id):
    data = {
        "user_ids" : vk_id,
        "fields"   : ["maiden_name"],
        "name_case": "nom"
    }
    async with session.post(
            f"{URL}users.get",
            ssl=True,
            data={**data, **DEFAULT_DATA},
    ) as response:
        res = await response.json()
        if "error" in res:
            return []
        return res["response"][0]


@client_exception_wrapper
async def get_group_id(session):
    async with session.post(
            f"{URL}groups.getById", ssl=True, data={**DEFAULT_DATA}
    ) as response:
        res = await response.json()
        return res["response"][0]


@client_exception_wrapper
async def create_chat(session, title):
    group_id = await get_group_id(session)
    data = {
        "title"   : title,
        "group_id": group_id["id"]
    }
    async with session.post(
            f"{URL}messages.createChat",
            ssl=True,
            data={**data, **DEFAULT_DATA},
    ) as response:
        res = await response.json()
        return res["response"]


@client_exception_wrapper
async def get_invite_link(session, peer_id, reset=1):
    group_id = await get_group_id(session)
    data = {
        "peer_id" : peer_id,
        "reset"   : reset,
        "group_id": group_id["id"]
    }
    async with session.post(
            f"{URL}messages.getInviteLink",
            ssl=True,
            data={**data, **DEFAULT_DATA},
    ) as response:
        res = await response.json()
        return res["response"]


@client_exception_wrapper
async def upload_photo(session, peer_id, file):
    upload_server = await get_upload_server(session, peer_id)

    form_data = FormData()
    form_data.add_field(
        'photo',
        BytesIO(file),
        content_type='multipart/form-data',
        filename="grid.png"
    )

    async with session.post(
            upload_server['upload_url'],
            data=form_data,
    ) as response:
        res = await response.json(content_type='text/html')
    vk_photo = await save_messages_photo(
        session,
        res['photo'],
        res['server'],
        res['hash'],
    )
    return f"photo{vk_photo['owner_id']}_{vk_photo['id']}"


@client_exception_wrapper
async def get_upload_server(session, peer_id):
    data = {
        "peer_id": peer_id
    }
    async with session.post(
            f"{URL}photos.getMessagesUploadServer",
            ssl=True,
            data={**data, **DEFAULT_DATA},
    ) as response:
        res = await response.json()
        return res['response']


@client_exception_wrapper
async def save_messages_photo(session, photo, server, photo_hash):
    data = {
        "photo": photo,
        "server": server,
        "hash": photo_hash,
    }
    async with session.post(
            f"{URL}photos.saveMessagesPhoto",
            ssl=True,
            data={**data, **DEFAULT_DATA},
    ) as response:
        res = await response.json()
        return res['response'][0]

