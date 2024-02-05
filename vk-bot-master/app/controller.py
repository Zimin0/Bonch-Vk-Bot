from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from app.db import Cache, User
from app.endpoint import Button, Endpoint
from app.vk import send_message


class State:
    db = None
    aiohttp_session = None
    message = None
    endpoint = None
    controller = None
    text = None

    def __init__(self, db, aiohttp_session, message):
        self.db = db
        self.aiohttp_session = aiohttp_session
        self.message = message


class Response:
    _keyboard = None

    def __init__(self, state):
        self._user_message = state.message
        self._controller = state.controller
        self._endpoint = state.main_endpoint
        self._text = state.text
        self._session = state.aiohttp_session

    def __add_default_buttons(self, keyboard):
        if self._endpoint == self._controller.default_endpoint:
            return keyboard
        if self._endpoint.keyboard:
            keyboard.add_line()
        keyboard.add_button(
            "Главная",
            color=VkKeyboardColor.NEGATIVE,
            payload={"action": "main"},
        )
        return keyboard

    def _process_button(self, button):
        if isinstance(button, Button):
            return button.generate()
        endpoint = self._controller.get_named_endpoint(button)
        assert endpoint, (
            f"Keyboard button {button} " f"should be declared as endpoint"
        )
        return endpoint.generate_as_button()

    def _add_additional_buttons(self, keyboard):
        for number, kb_tr in enumerate(self._endpoint.keyboard):
            if number > 0:
                keyboard.add_line()
            for kb_td in kb_tr:
                keyboard.add_button(**self._process_button(kb_td))
        return keyboard

    @property
    def keyboard(self):
        if self._keyboard:
            return self._keyboard
        keyboard = VkKeyboard()

        if self._endpoint.keyboard:
            keyboard = self._add_additional_buttons(keyboard)

        keyboard = self.__add_default_buttons(keyboard)

        self._keyboard = keyboard.get_keyboard()
        return self._keyboard

    async def send(self, text=None, attachment=None):
        data = {
            "peer_id": self._user_message.peer_id,
            "message": self._endpoint.description,
            "keyboard": self.keyboard,
            "attachment": self._endpoint.attachment
        }
        if text:
            data["message"] = text
            data["attachment"] = None
        await send_message(self._session, data)


class Controller:
    _default_endpoint = None

    def __init__(self):
        self._endpoints_by_name = {}
        self._keys_by_title = {}

    def add_endpoint(self, endpoint: Endpoint, as_default=False):
        assert (
            endpoint.name not in self._endpoints_by_name
        ), f"Endpoint with name {endpoint.name} already exists"
        self._endpoints_by_name[endpoint.name] = endpoint
        self._keys_by_title[endpoint.title.lower()] = endpoint.name
        if as_default:
            self._default_endpoint = endpoint

    @property
    def default_endpoint(self):
        return self._default_endpoint

    def get_cached_endpoint(self, peer_id):
        key = Cache.get(f"state_key_{peer_id}")
        if key:
            Cache.delete(f"state_key_{peer_id}")
            return self._endpoints_by_name[key]
        return None

    def get_named_endpoint(self, name):
        if name in self._endpoints_by_name:
            return self._endpoints_by_name[name]
        return None

    def get_titled_endpoint(self, title):
        if title.lower() in self._keys_by_title:
            return self._endpoints_by_name[self._keys_by_title[title.lower()]]
        return None

    def get_endpoint(self, message):
        methods = (
            ("get_named_endpoint", "payload_action"),
            ("get_cached_endpoint", "peer_id"),
            ("get_titled_endpoint", "text"),
        )
        for method in methods:
            endpoint = getattr(self, method[0])(getattr(message, method[1]))
            if endpoint:
                return endpoint
        return self.default_endpoint

    @staticmethod
    async def get_user(state):
        return await User.find_or_create(state)

    @staticmethod
    async def _get_response_endpoint(state):
        endpoint = state.main_endpoint
        while True:
            _endpoint = await endpoint.handler(state)
            if isinstance(_endpoint, Endpoint):
                endpoint = _endpoint
                continue
            return endpoint

    async def handle(self, state):
        user = await self.get_user(state)
        user.set_vk_id(state.message.peer_id)
        state.user = user

        state.controller = self

        endpoint = self.get_endpoint(state.message)

        state.main_endpoint = endpoint

        endpoint = await self._get_response_endpoint(state)
        state.main_endpoint = endpoint

        response = Response(state)
        await response.send()

        return response
