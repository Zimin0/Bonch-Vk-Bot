import logging
import uuid

from app.db.utils import BaseListModel, BaseModel, Time
from app.settings import CORE_API_URL, VK_CONF_ID
from app.vk import create_chat, get_invite_link

logger = logging.getLogger(__name__)


class EducationalType(BaseListModel):
    URL = CORE_API_URL + "users/educational-type/"
    CACHING = True
    TTL = Time.HOURS_168


class EducationalLocation(BaseListModel):
    URL = CORE_API_URL + "users/educational-location/"
    CACHING = True
    TTL = Time.HOURS_1


class EducationalInstitutions(BaseListModel):
    URL = CORE_API_URL + "users/educational-institutions/"
    CACHING = True
    TTL = Time.MINUTES_3


class EducationalInstitution(BaseModel):
    URL = CORE_API_URL + "users/educational-institutions/"
    CACHING = True
    TTL = Time.MINUTES_30


class UserVerificationRequests(BaseListModel):
    URL = CORE_API_URL + "users/verification-request/"
    CACHING = True
    TTL = Time.MINUTES_3


class UserVerificationRequest(BaseModel):
    URL = CORE_API_URL + "users/verification-request/"
    CACHING = True
    TTL = Time.MINUTES_3

    @staticmethod
    async def create_chat(session):
        # verif_requests = await UserVerificationRequests.all(session)
        number = str(uuid.uuid1()).split('-')
        chat_name = f"Заявка №{number[0]}"

        peer_id = await create_chat(session, chat_name)
        link = await get_invite_link(session, VK_CONF_ID + peer_id)
        return link["link"]
