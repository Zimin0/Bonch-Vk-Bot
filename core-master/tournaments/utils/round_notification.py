import logging

from users.models import Notification, UserNotification

logger = logging.getLogger(__name__)


def create_round_notification(text, user_id, endpoint=None):
    """Отправка уведомления пользователю"""
    notification = Notification(
        text=text,
        endpoints=endpoint,
        type=Notification.PERSONAL,
        system=True
    )
    notification.save()
    user_notification = UserNotification(
        user=user_id,
        notification=notification,
    )
    try:
        user_notification.save()
    except Exception as e:
        logger.exception(e)


def next_round(instance, teams_and_captains):
    """Уведомления о доступности следующего раунда"""
    for team in teams_and_captains:
        data = {"id": instance.match.tournament.id, "team_id": team}

        create_round_notification(
            "Доступен следующий раунд!",
            teams_and_captains[team],
            [
                {
                    "name": "tournament_happening",
                    "title": "Посмотреть",
                    "payload": data,
                }
            ],
        )


def create_winner_notification(instance, teams_and_captains, payload):
    """Уведомлени для победителя матча"""
    if instance.match.number == 1:
        text = (
            f"Поздравляю, вы выиграли турнир"
            f" {instance.match.tournament.name}"
        )
    else:
        text = "Вы выиграли матч!"

    create_round_notification(
        text,
        teams_and_captains[instance.match.winner],
        payload,
    )


def create_notification_of_found_opponent(instance, payload):
    """Уведомления для соперника следующего матча"""
    if instance.match.next_match_for_winner:
        next_match_teams = list(instance.match.next_match_for_winner.teams)
        opponent_captain = [
            team.captain
            for team in next_match_teams
            if team.id != instance.match.winner
        ]

        if opponent_captain:
            create_round_notification(
                "Ваш соперник определен!",
                opponent_captain[0],
                payload,
            )


def create_loser_notification(instance, teams_and_captains):
    """Уведомления для проигравшего в матче"""
    del teams_and_captains[instance.match.winner]
    loser = list(teams_and_captains.values())
    if instance.match.next_match_for_loser:
        create_round_notification("Доступен следующий матч в нижней сетке!",
                                  loser[0])
    else:
        create_round_notification("Для вас турнир окончен", loser[0])


def next_match(instance, teams_and_captains):
    """Уведомления при завершении матча"""
    winner_payload = [
        {
            "name": "tournament",
            "title": "Посмотреть",
            "payload": {"id": instance.match.tournament.id, "info": "grid"},
        }
    ]
    create_winner_notification(instance, teams_and_captains, winner_payload)
    create_loser_notification(instance, teams_and_captains)
    create_notification_of_found_opponent(instance, winner_payload)


def generating_round_notifications(instance):
    """Уведомления при завершении раунда"""
    teams_and_captains = {
        team.id: team.captain for team in instance.teams.all()
    }
    if instance.match.winner:
        next_match(instance, teams_and_captains)
    else:
        next_round(instance, teams_and_captains)
