from cyberbot.celery import app
from tournaments.models import Tournament
from tournaments.utils import TournamentGridSingle
from tournaments.utils.tournament_double_grid import TournamentDoubleGRid
from users.models import Notification, User, UserNotification

text_dict = {
    3: "Турнир {name}, по игре {game}, начался",
    2: "Началась стадия подтверждения "
       "участия на турнир {name}, по игре {game}",
    1: "Началась регистрация на турнир {name}, по игре {game}",
}


def get_users_for_notification(event_type, tournament):
    users = []
    if event_type == 1:
        users = User.objects.all()
    if event_type == 2:
        teams = tournament.registered_teams.all()
        users = [team.captain for team in teams]
    if event_type == 3:
        teams = tournament.confirmed_teams.all()
        users = [team.captain for team in teams]
    return users


@app.task(bind=True)
def generating_tournament_grid(*args, **kwargs):
    # pylint: disable=unused-argument
    if "tournament_id" in kwargs:
        tournament = Tournament.objects.filter(
            id=kwargs["tournament_id"]
        ).first()
        if not list(tournament.matches.all()):
            if tournament.grid == tournament.SINGLE:
                tournament = TournamentGridSingle(tournament)
                if tournament.start_tournament():
                    tournament.primary_draw_of_teams()

            elif tournament.grid == tournament.DOUBLE:
                grid = TournamentDoubleGRid(
                    tournament.confirmed_teams.all(),
                    tournament
                )

                grid.generation_winner_bracket()
                grid.generation_loser_bracket()
                grid.add_teams()
                grid.save_grid()
                grid.create_match_relations()
                grid.add_rounds()


@app.task(bind=True)
def create_tournament_event_notification(*args, **kwargs):
    # pylint: disable=unused-argument
    tournament_id = kwargs.get("tournament_id")
    event_type = kwargs.get("event_type")
    tournament = Tournament.objects.get(id=tournament_id)
    text = text_dict[event_type].format(
        **{"name": tournament.name,
           "game": tournament.game.name}
    )
    notification = Notification.objects.filter(text=text).first()
    if not notification:
        notification = Notification(
            text=text,
            endpoints=[
                {
                    "name": "tournament",
                    "title": "Посмотреть",
                    "payload": {"id": tournament_id},
                }
            ],
            type=Notification.MAILING,
            system=True,
        )
        notification.save()
    users = get_users_for_notification(event_type, tournament)
    for user in users:
        if (tournament.game in user.game_subscription.all()) \
                or (event_type > 1):
            user_notification = UserNotification(
                user=user, notification=notification
            )
            try:
                user_notification.save()
            except Exception as e:
                print(e)
                print("znachit ne doidet soobshenie")
