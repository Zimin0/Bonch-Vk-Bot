import logging
import time
import traceback

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.controller import State
from app.db import InputMessage, SessionLocal, User
from app.notifications import Notification
from app.router import controller
from app.schemes import Notification as NotificationSchema
from app.schemes import VKRequest
from app.settings import VK_TOKEN_CONFIRMATION

app = APIRouter(prefix="/bot", tags=["VK Bot"])
logger = logging.getLogger(__name__)


def get_db(request: Request):
    return request.state.db


def get_aiohttp_session(request: Request):
    return request.state.db


@app.post("/")
async def index(
    message: VKRequest, db: SessionLocal = Depends(get_db)
) -> Response:
    if message.type == "confirmation":
        return Response(content=VK_TOKEN_CONFIRMATION)

    if not message.type == "message_new":
        raise HTTPException(status_code=400, detail="Incorrect message type")

    try:
        if message.object.message.peer_id == message.object.message.from_id:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                state = State(db, session, InputMessage(message.object.message))
                await controller.handle(state)
    except Exception as e:
        logger.exception(e)
        print(traceback.format_exc())

    return Response(content="ok")


@app.post("/notifications/")
async def create_notifications(
    raw_notification: NotificationSchema, db: SessionLocal = Depends(get_db)
) -> str:
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        state = State(db, session, raw_notification)
        notification = Notification(raw_notification)
        await notification.send(state)
        return "ok"

    # print(res.status)
    # return 400, "ok"
