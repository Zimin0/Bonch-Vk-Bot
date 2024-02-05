from typing import List, Optional

from pydantic import BaseModel


class VKMessage(BaseModel):
    text: str
    peer_id: int
    from_id: int
    payload: str = None
    date: int
    id: int
    attachments: list
    conversation_message_id: int


class VKObject(BaseModel):
    message: VKMessage
    client_info: dict


class VKRequest(BaseModel):
    object: VKObject = None
    secret: str = None
    type: str
    group_id: int


class Endpoint(BaseModel):
    name: str
    title: str
    payload: Optional[dict]


class Notification(BaseModel):
    core_id: int
    text: str
    attachments: Optional[list]
    endpoints: Optional[List[Endpoint]]
