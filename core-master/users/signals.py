import logging
from json import JSONDecodeError

import requests
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from cyberbot.settings import CLASH_ROYALE_API_TOKEN
from games.models import Game, PlayerCount
from teams.models import Team
from users.models import GameAccount, Notification, UserNotification

logger = logging.getLogger(__name__)

HEADERS = {
    "clash_royale": {
        "Authorization": f"Bearer {CLASH_ROYALE_API_TOKEN}",
        "Accept": "application/json",
    }
}


class UserNotFound(Exception):
    pass


def get_clash_response(user_id):
    try:
        response = requests.get(
            f"https://api.clashroyale.com/v1/players/{user_id}",
            headers=HEADERS["clash_royale"],
        ).json()
    except requests.ConnectionError as err:
        logger.exception(err)
        return None
    except JSONDecodeError as err:
        logger.exception(f"Error: \n{err}")
        return None
    else:
        return response


def create_single_teams(instance, team_name):
    res = []
    player_count = PlayerCount.objects.get(count=1)
    for game in Game.objects.filter(
            platform=instance.platform, player_count=player_count
    ).all():
        new_team_name = None
        if game.name == 'Clash Royale':
            new_team_name = team_name + "   "
        elif game.name == 'Dota 2':
            new_team_name = team_name + "    "
        elif game.name == 'CS GO':
            new_team_name = team_name + "     "
        elif game.name == 'Hearthstone':
            new_team_name = team_name + "      "
        if new_team_name:
            team = Team.objects.filter(captain=instance.user,
                                       game=game,
                                       players_count=1).first()
            if team:
                if team.name != new_team_name:
                    team.name = new_team_name
                    team.save()
                continue

            if game.name in ('Clash Royale', 'Dota 2', 'Hearthstone'): #TODO: подключить CS GO, Hearthstone
                user_team = Team(
                    name=f'{new_team_name}',
                    captain=instance.user,
                    game=game,
                    players_count=1,
                )
                user_team.save()
                user_team.players.add(user_team.captain)
                res.append(user_team)
    return res


@receiver(pre_save, sender=GameAccount)
def create_clash_royale(
        sender, instance, **kwargs
):  # pylint: disable=unused-argument
    if not instance.platform.name == "Clash Royale":
        return None
    user_id = instance.platform_token.replace("#", "%23")
    response = get_clash_response(user_id.upper())

    print(response)
    if "reason" in response:
        logger.exception(response["reason"])
        raise UserNotFound
    try:
        instance.nick_name = f'{response["name"]}'
        create_single_teams(instance, response["name"])
    except KeyError as err:
        logger.exception(err)
        return None
    return instance


@receiver(post_save, sender=GameAccount)
def create_game_acc_notification(instance, **__):
    text = f"Ваш ник в {instance.platform.name}: {instance.nick_name}"
    notification = Notification(
        text=text,
        system=True
    )
    notification.save()
    user_notification = UserNotification(
        user=instance.user,
        notification=notification
    )
    user_notification.save()


@receiver(post_save, sender=GameAccount)
def create_steam_acc(instance, **__):
    user_steam_name = instance.nick_name
    create_single_teams(instance, user_steam_name)
    return instance
