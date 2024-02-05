import logging
import time
from datetime import datetime

from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from users.models import Notification, UserNotification

logger = logging.getLogger(__name__)


class Team(models.Model):
    name = models.CharField(
        max_length=500,
        verbose_name="Название команды",
        null=False,
        unique=True,
    )
    captain = models.ForeignKey(
        "users.User",
        verbose_name="Капитан команды",
        related_name="teams_captaining",
        null=False,
        on_delete=models.CASCADE,
    )
    players = models.ManyToManyField(
        "users.User",
        verbose_name="Члены команды",
        related_name="teams",
        blank=True,
    )
    game = models.ForeignKey(
        "games.Game",
        verbose_name="Игра команды",
        related_name="teams",
        null=False,
        on_delete=models.CASCADE,
    )
    players_count = models.IntegerField(
        verbose_name="Количество игроков в команде", null=False, default=5
    )
    archived = models.BooleanField(verbose_name="Архивирована", default=False)

    @property
    def allow_chang(self):
        for tournament in self.confirmed_teams.all():
            for match in tournament.matches.all():
                if self in match.teams:
                    if not match.is_playing:
                        return False
        return True

    @property
    def platform(self):
        return f"{self.game.platform.name}"

    @property
    def study_team(self):
        edu = [player.educational_institution.institute
               for player in self.players.all()]
        return len(set(edu)) <= 1

    @property
    def user_team_info(self):
        res = ''
        for player in self.players.all():
            res += "-" * 50 + "\n"
            res += f"Игрок: {player}\n"
            res += f"____Верификация: {player.verified}\n"
            res += f"____Образование: {player.educational_institution}\n"
            res += f"____Игровые аккаунты: \n"
            for acc in player.accounts.all():
                res += f"________{acc.platform}: {acc.nick_name}\n"
        return res

    def __str__(self):
        return f"{self.name}"


class TeamInvites(models.Model):
    NEW = 1
    CHECKED = 2
    STATUSES = ((NEW, "новое"), (CHECKED, "просмотренное"))
    team = models.ForeignKey(
        Team,
        models.CASCADE,
        verbose_name="Команда",
        null=False,
    )
    user = models.ForeignKey(
        "users.User",
        models.CASCADE,
        verbose_name="Игрок",
        null=False,
    )
    date = models.DateTimeField(
        verbose_name="Дата приглашения", default=datetime.utcnow
    )
    type = models.IntegerField(choices=STATUSES, null=False, default=NEW)

    @property
    def expired(self):
        now = timezone.now()
        count_time = (time.mktime(now.timetuple()) -
                      time.mktime(self.date.timetuple()))
        if count_time > 86000:
            return False
        return True

    @property
    def team_name(self):
        return self.team.name

    @property
    def team_game(self):
        return self.team.game.name

    def __str__(self):
        return f"{self.team}"


@receiver(post_save, sender=TeamInvites)
def send_team_invites(instance, **__):
    print(instance.team)
    print(instance.user)
    if instance.type == TeamInvites.NEW:
        logger.info(f'{instance.user} пришло приглашение в '
                    f'команду "{instance.team}"')
        print(f'Вам пришло приглашение в '
              f'команду по "{instance.team_game}"')
        text = f'Вам пришло приглашение в ' \
               f'команду по "{instance.team_game}"'
        buttons = [{
            "name": "team_add_player_invite",
            "title": "Посмотреть",
            "payload": {
                "invite_id": instance.id
            },
        }]
        notification = Notification(
            text=text,
            endpoints=buttons,
            system=True
        )
        notification.save()
        user_notification = UserNotification(
            user=instance.user,
            notification=notification,
            delivery_date=notification.date_created,
        )
        user_notification.save()
    else:
        logger.info(f'{instance.user} не пришло приглашение в '
                    f'команду "{instance.team} {instance.type} '
                    f'{TeamInvites.NEW}"')


@receiver(post_save, sender=Team)
def update_stock(sender, instance, **kwargs):
    if instance.archived:
        users = instance.players.all()

        notification = Notification(
            text=f'Команда "{instance.name}" по игре "{instance.game.name}"'
                 f' расформирована',
            type=Notification.MAILING,
            system=True
        )
        notification.save()
        for user in users:
            user_notification = UserNotification(
                user=user,
                notification=notification,
            )
            user_notification.save()


@receiver(post_save, sender=Team)
def team_players_change(update_fields, instance, **kwargs):
    if update_fields:
        if 'captain' in update_fields:
            text = (
                f'В команде "{instance.name}" новый капитан - '
                f'"{instance.captain}"'
            )
            notification = Notification(
                text=text,
                type=Notification.PERSONAL,
                system=True
            )
            notification.save()
            for user in instance.players.all():
                if user != instance.captain:
                    user_notification = UserNotification(
                        user=user,
                        notification=notification,
                    )
                    user_notification.save()


@receiver(m2m_changed, sender=Team.players.through)
def team_players_change(action, model, pk_set, instance, **__):
    if 'post' in action:
        for user_id in pk_set:
            user = model.objects.get(id=user_id)

            if action == 'post_add':
                text_for_team = (
                    f'Игрока "{user.first_name} {user.last_name}" '
                    f'добавили в вашу команду "{instance.name}"'
                )
                notification = Notification(
                    text=text_for_team,
                    type=Notification.PERSONAL,
                    system=True
                )
                notification.save()

            elif action == 'post_remove':
                text = f'Вы больше не состоите в команде "{instance.name}"'

                notification = Notification(
                    text=text,
                    type=Notification.PERSONAL,
                    system=True
                )
                notification.save()

                user_notification = UserNotification(
                    user=user,
                    notification=notification,
                )
                user_notification.save()

                text_for_team = (
                    f'Игрока "{user.first_name} {user.last_name}" '
                    f'исключили из вашей команды "{instance.name}"'
                )
                notification = Notification(
                    text=text_for_team,
                    type=Notification.PERSONAL,
                    system=True
                )
                notification.save()

            for user in instance.players.all():
                if user.id != user_id:
                    user_notification = UserNotification(
                        user=user,
                        notification=notification,
                    )
                    user_notification.save()
