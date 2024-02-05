from vk_api.keyboard import VkKeyboard

from app.db.models import LocalUser
from app.vk import send_message


class Notification:
    def __init__(self, raw):
        self.core_id = raw.core_id
        self.text = raw.text
        self._attachments = raw.attachments
        self.endpoints = raw.endpoints

    @property
    def attachment(self):
        return ",".join(self._attachments)

    def _generate_keyboard(self):
        vk_keyboard = VkKeyboard(inline=True)
        for x, endpoint in enumerate(self.endpoints):
            if x > 0:
                vk_keyboard.add_line()
            vk_keyboard.add_button(
                label=endpoint.title,
                payload={"action": endpoint.name, "data": endpoint.payload},
            )
        return vk_keyboard.get_keyboard()

    @property
    def keyboard(self):
        if not self.endpoints:
            return None
        return self._generate_keyboard()

    async def send(self, state):
        local_user = await LocalUser.find_by_core_id(state, self.core_id)
        if local_user:
            data = {
                "peer_id": local_user.vk_id,
                "message": self.text,
                "keyboard": self.keyboard,
            }
            await send_message(state.aiohttp_session, data)
