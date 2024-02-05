import json

from sqlalchemy import Column, Integer, Text

from app.db.setup import Base
from app.vk import get_vk_user_by_id


class User(Base):
    core_id = Column(Integer)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)

    @classmethod
    async def create(cls, state):
        raw_user = await get_vk_user_by_id(
            state.aiohttp_session, state.message.peer_id
        )
        user = cls(
            vk_id=raw_user["id"],
            first_name=raw_user["first_name"],
            last_name=raw_user["last_name"],
        )
        state.db.add(user)
        state.db.commit()
        return user

    @classmethod
    async def find(cls, state):
        return (
            state.db.query(User).filter_by(vk_id=state.message.peer_id).first()
        )

    @classmethod
    async def find_by_core_id(cls, state, core_id):
        return state.db.query(User).filter_by(core_id=core_id).first()

    @classmethod
    async def find_by_vk_id(cls, state, vk_id):
        return state.db.query(User).filter_by(vk_id=vk_id).first()

    @classmethod
    async def find_or_create(cls, state):
        user = await cls.find(state)
        if not user:
            user = await cls.create(state)
        return user


class InputMessage:
    _fixed_payload = {}
    peer_id = None
    text = None
    from_id = None
    date = None
    id = None
    attachments = None

    def __init__(self, message):
        self.peer_id = message.peer_id
        self._payload = message.payload
        self.text = message.text
        self.from_id = message.from_id
        self.date = message.date
        self.id = message.id
        self.attachments = message.attachments

    @property
    def fixed_payload(self):
        if not self._fixed_payload:
            if self._payload:
                try:
                    self._fixed_payload = json.loads(self._payload)
                except json.JSONDecodeError:
                    self._fixed_payload = {}
        return self._fixed_payload

    @property
    def payload_action(self):
        return self.fixed_payload.get("action")

    @property
    def payload_data(self):
        return self.fixed_payload.get("data")
