import logging

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ParseError

from tournaments.models import (
    TournamentNotification,
    Round,
    TournamentEvent,
    Tournament, CsgoPeakStage
)
from tournaments.utils import (
    TournamentGridSingle,
    generating_round_notifications,
    update_periodic_task
)
from tournaments.views import Notification, UserNotification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TournamentNotification)
def tournament_notifications(instance, **__):
    if (instance.users_status < TournamentNotification.NONE) and instance.send:
        user_notification_model = apps.get_model("users", "UserNotification")
        notification_model = apps.get_model("users", "Notification")
        if instance.users_status == TournamentNotification.REGISTRATION:
            users = instance.tournament.registration_users()
        elif instance.users_status == TournamentNotification.PLAYING:
            users = instance.tournament.confirmed_users()
        else:
            users = []
        notification = notification_model(
            text=instance.text,
            type=notification_model.MAILING,
            system=True,
        )
        notification.save()
        for user in users:
            tmp = user_notification_model.objects.filter(
                user=user,
                notification=notification,
            ).first()

            if not tmp:
                user_notification = user_notification_model(
                    user=user,
                    notification=notification,
                    delivery_date=instance.date_created
                )
                user_notification.save()

        instance.send = False
        instance.save()


@receiver(post_save, sender=Round)
def update_stock(instance, **__):
    generating_round_notifications(instance)
    tournament = TournamentGridSingle(instance.match.tournament)
    tournament.update_grid()


@receiver(post_save, sender=TournamentEvent)
def event_notifications(instance, **__):
    update_periodic_task(instance)


@receiver(m2m_changed, sender=Round.teams.through)
def round_team_players_change(instance, **kwargs):
    if kwargs['action'] == 'pre_add':
        tournament_teams = instance.match.tournament.confirmed_teams.all()
        for team_id in list(kwargs['pk_set']):
            team = kwargs['model'].objects.get(id=team_id)
            if team not in tournament_teams:
                raise ValidationError(
                    f'Команда "{team}" не участвует в этом турнире, '
                    "нельзя ее добавить в этот раунд"
                )


@receiver(m2m_changed, sender=Tournament.confirmed_teams.through)
def tournament_add_confirmed_team(action, model, pk_set, instance, **__):
    if action == 'post_add':
        user_notification_model = apps.get_model("users", "UserNotification")
        notification_model = apps.get_model("users", "Notification")
        for team_id in pk_set:
            team = model.objects.filter(id=team_id).first()

            reg_team = instance.registered_teams.all()
            if team in reg_team:
                if team.players_count == 1:
                    text = (
                        f'Вы подтверили участие в турнире "{instance.name}" '
                        f'на аккаунте "{team.name}".'
                    )
                else:
                    text = (f'Ваша команда "{team.name}" подтвердила '
                            f'участие в турнире "{instance.name}"')
                notification = notification_model(
                    text=text,
                    type=notification_model.MAILING,
                    system=True,
                )
            else:
                notification = notification_model(
                    text=(f'Вашу команду "{team.name}" пригласили '
                          f'участвовать в турнире "{instance.name}"'),
                    type=notification_model.MAILING,
                    system=True,
                )

            notification.save()
            users = team.players.all()
            for user in users:
                user_notification = user_notification_model(
                    user=user,
                    notification=notification
                )
                try:
                    user_notification.save()
                except Exception as e:
                    logger.exception(e)


@receiver(m2m_changed, sender=Tournament.registered_teams.through)
def tournament_add_registered_team(action, instance, **__):
    if action == 'pre_add':
        if instance.max_teams <= len(instance.registered_teams.all()):
            raise ParseError(detail="team limit", code=400)


@receiver(m2m_changed, sender=Tournament.registered_teams.through)
def tournament_add_registered_team(action, model, pk_set, instance, **__):
    if action == 'post_add':
        user_notification_model = apps.get_model("users", "UserNotification")
        notification_model = apps.get_model("users", "Notification")
        for team_id in pk_set:
            team = model.objects.filter(id=team_id).first()

            notification = notification_model(
                text=(f'Ваша команда "{team.name}" зарегестрировалась '
                      f'на турнир "{instance.name}"'),
                type=notification_model.MAILING,
                system=True,
            )
            notification.save()
            users = team.players.all()
            for user in users:
                user_notification = user_notification_model(
                    user=user,
                    notification=notification
                )
                try:
                    user_notification.save()
                except Exception as e:
                    logger.exception(e)


@receiver(post_save, sender=Tournament)
def update_matches(instance, **__):
    if instance.winner or instance.archived:
        matches = instance.matches.all()
        for match in matches:
            match.archived = True
            match.save()


@receiver(post_save, sender=CsgoPeakStage)
def csgo_peak_notification(instance, **__):
    teams = instance.match.teams.copy()
    teams.remove(instance.team)
    notification = Notification.objects.create(
        text="Ваша очередь выбирать карту!",
        type=Notification.PERSONAL,
        system=True,
        endpoints=[{
            "name": "tournament_csgo_peak_stage_select_map",
            "title": "Посмотреть",
            "payload": {'team': {'id': teams[0].id,
                                 'name': teams[0].name},
                        'match': instance.match.id}
        }]
    )
    UserNotification.objects.create(
        user=teams[0].captain,
        notification=notification
    )
