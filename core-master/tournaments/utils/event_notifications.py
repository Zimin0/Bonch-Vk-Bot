import json

from django_celery_beat.models import ClockedSchedule, PeriodicTask


def create_task(name, data, clock, task):
    periodic_task = PeriodicTask.objects.filter(name=name).first()
    if periodic_task:
        periodic_task.delete()
    periodic_task = PeriodicTask(
        task=task,
        name=name,
        clocked=clock,
        enabled=True,
        one_off=True,
        kwargs=json.dumps(data),
    )
    periodic_task.save()


def update_periodic_task(event, send_notification=True):
    clock = ClockedSchedule(clocked_time=event.time_start)
    clock.save()
    if event.send_notification:
        if send_notification:
            create_task(
                f"{event.tournament.name}_{event.type}_event_mailing",
                {"tournament_id": event.tournament.id, "event_type": event.type},
                clock,
                "tournaments.tasks.create_tournament_event_notification",
            )
        event.send_notification = False
        event.save()
    if event.type == 2:
        clock = ClockedSchedule(clocked_time=event.time_end)
        clock.save()
        create_task(
            f"{event.tournament.name}_grid_generation",
            {"tournament_id": event.tournament.id},
            clock,
            "tournaments.tasks.generating_tournament_grid",
        )
