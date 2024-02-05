from vk_api.keyboard import VkKeyboardColor


class Endpoint:
    def __init__(
        self,
        name: str,
        title: str,
        description: str,
        handler: callable,
        keyboard: [list, None],
        payload: [dict, None] = None,
        attachment: str = None
    ):
        self.name = name
        self.title = title
        self.description = description
        self.handler = handler
        self.keyboard = keyboard
        self.payload = payload
        self.attachment = attachment

    def generate_as_button(self):
        return Button(
            name=self.name,
            title=self.title,
            payload=self.payload,
        ).generate()


class Button:
    def __init__(
        self, name, title, payload=None, color=VkKeyboardColor.SECONDARY
    ):
        self.name = name
        self.title = title
        self.payload = payload
        self.color = color

    def generate(self):
        return {
            "label": self.title,
            "color": self.color,
            "payload": {"action": self.name, "data": self.payload},
        }


class BackwardButton(Button):
    def __init__(self, name, payload=None):
        super().__init__(
            name, title="Назад", payload=payload, color=VkKeyboardColor.PRIMARY
        )
