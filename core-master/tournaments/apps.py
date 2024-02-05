from django.apps import AppConfig


class TournomentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tournaments"

    def ready(self):
        import tournaments.signals
