from django.db import models


class PlayerCount(models.Model):
    count = models.IntegerField("Количество игроков", null=False,)

    def __str__(self):
        return f"<PlayerCount - {self.count}>"


class Game(models.Model):
    name = models.CharField(
        max_length=250, verbose_name="Название игры", null=False
    )
    description = models.CharField(
        max_length=1000, verbose_name="Описание игры", null=True
    )
    platform = models.ForeignKey(
        "users.Platform",
        verbose_name="Платформа игры",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    player_count = models.ManyToManyField(
        PlayerCount,
        blank=False,
        verbose_name="количество игроков в команде",
    )

    @property
    def players_count(self):
        res = [obj.count for obj in self.player_count.all()]
        return res

    def __repr__(self):
        return f"<Game - {self.name} for platform {self.platform}>"

    def __str__(self):
        return f"{self.name}"
