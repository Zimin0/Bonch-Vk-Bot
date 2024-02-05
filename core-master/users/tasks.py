import logging
import random
import time

import requests

from cyberbot import settings
from cyberbot.celery import app
from cyberbot.settings import VK_BOT_URL
from .models import UserNotification, GameAccount
from .serializers import UserNotificationSerializer

logger = logging.getLogger(__name__)


@app.task(bind=True)
def update_steam_nickname(*_, **__):
    game_acc = GameAccount.objects.filter(platform__name='Steam').all()
    for acc in game_acc:
        time.sleep(random.uniform(0, 5))
        steam_ids = acc.platform_token
        url = settings.STEAM_URL + "ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            "key": settings.STEAM_KEY,
            "steamids": steam_ids,
        }
        response = requests.get(url, params=params)
        if response.status_code < 300:
            response = response.json()
            if response['response']['players']:
                user_acc = response['response']['players'][0]
                steam_name = user_acc['personaname']
                try:
                    if acc.nick_name != steam_name:
                        acc.nick_name = steam_name
                        acc.save()
                except Exception as e:
                    logger.exception(e)
                    print(e)


@app.task(bind=True)
def send_user_notifications(*_, **kwargs):
    notification_id = kwargs.get("id")
    if notification_id:
        user_notifications = UserNotification.objects \
            .filter(id=notification_id).first()
        if user_notifications:
            if user_notifications.status in [UserNotification.NEW,
                                             UserNotification.FAIL]:
                user_notifications.set_sending()
                data = UserNotificationSerializer.export(user_notifications)
                try:
                    with requests.post(
                            VK_BOT_URL + "bot/notifications/", json=data
                    ) as response:
                        if response.status_code < 300:
                            user_notifications.set_done()
                except Exception as e:
                    logger.exception(e)
                    print(e)
                    user_notifications.set_fail()

