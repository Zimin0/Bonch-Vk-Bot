import json
import uuid
from datetime import datetime, date

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime, now
from django_celery_beat.models import ClockedSchedule, PeriodicTask


class User(models.Model):
    NOTIFICATION = 1
    GAME_ACC = 2
    EDUCATION = 3
    DONE = 4
    STATUSES = (
        (NOTIFICATION, "Настройка уведомлений"),
        (GAME_ACC, "Привязка игровый аккаунтов"),
        (EDUCATION, "Привязка учебного заведения"),
        (DONE, "Главное меню"),
    )
    """User model"""

    first_name = models.CharField(
        max_length=128, verbose_name="Имя", null=False
    )
    last_name = models.CharField(
        max_length=128, verbose_name="Фамилия", null=False
    )
    middle_name = models.CharField(
        max_length=128,
        verbose_name="Отчество",
        null=True,
        blank=True,
        default="",
    )
    birth = models.DateField(
        verbose_name="Дата рождения", null=True, blank=True
    )
    educational_institution = models.ForeignKey(
        "UserEducation",
        verbose_name="Место учебы",
        related_name="users",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    roles = models.ManyToManyField(
        "UserRole",
        verbose_name="Роль пользователя на платформе",
        blank=True,
        related_name="users",
    )
    date_next_verification = models.DateField(
        "дата следующей верификации",
        blank=False,
        default=date.today
    )
    game_subscription = models.ManyToManyField(
        "games.Game",
        verbose_name="Игры по который пользователь будет получать уведомления",
        blank=True,
        related_name="users",
    )
    registration_sate = models.IntegerField(
        choices=STATUSES,
        default=NOTIFICATION
    )
    vk_id = models.CharField(
        "вк id",
        max_length=240,
        null=True,
        blank=True,
    )

    @property
    def federal_districts(self):
        if self.educational_institution:
            return self.educational_institution.location.federal_districts

    @property
    def location(self):
        if self.educational_institution:
            return self.educational_institution.location

    @property
    def verified(self):
        today_date = localtime(now()).date()
        if today_date >= self.date_next_verification:
            return False
        return True

    @property
    def platforms(self):
        return {
            account.platform: account.nick_name
            for account in self.accounts.all()
        }

    @property
    def game_acc(self):
        return {
            account.platform.name: account.nick_name
            for account in self.accounts.all()
        }

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserVerificationRequest(models.Model):
    """Заявки на верификацю"""

    user = models.ForeignKey(User, verbose_name="Пользователь",
                             null=False, on_delete=models.CASCADE)
    vk_chat_link = models.TextField(
        "Ссылка на беседу вк",
        null=False,
    )
    archived = models.BooleanField(verbose_name="Архивирована", default=False)

    def __str__(self):
        return f"{self.user}"


class Institute(models.Model):
    name = models.CharField(
        max_length=500, verbose_name="Название учебного заведения", null=False
    )

    def __str__(self):
        return f"{self.name}"


class UserEducation(models.Model):
    """Место учебы"""

    location = models.ForeignKey(
        "Location",
        verbose_name="Локация",
        related_name="user_education",
        on_delete=models.CASCADE,
        null=False,
    )
    type = models.ForeignKey(
        "EducationalType",
        verbose_name="Тип",
        related_name="user_education",
        on_delete=models.CASCADE,
        null=False,
    )
    institute = models.ForeignKey(
        "Institute",
        verbose_name="Учебное заведение",
        related_name="user_education",
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"{self.type} {self.location} {self.institute}"


class EducationalType(models.Model):
    """тип учебного заведения"""

    name = models.CharField(
        max_length=100, verbose_name="Название типа учебного заведения"
    )

    def __str__(self):
        return f"{self.name}"


class FederalDistricts(models.Model):
    """Федеральные округа Российской Федерации"""

    name = models.CharField(
        max_length=200, verbose_name="Название населенного пункта"
    )

    def __str__(self):
        return f"{self.name}"


class Location(models.Model):
    """субъекты федирации"""

    name = models.CharField(
        max_length=200, verbose_name="Название населенного пункта"
    )
    federal_districts = models.ForeignKey(
        FederalDistricts,
        verbose_name="Федеральный округ",
        related_name="federation_subjects",
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.name}"


class UserRestriction(models.Model):
    """заблокирован/не заблокирован"""

    user = models.ManyToManyField(
        User, verbose_name="Пользователь", related_name="restrictions"
    )
    reason = models.TextField(
        verbose_name="Причина блокировки", default="Отсутствует"
    )
    date_blocked = models.DateField(
        verbose_name="Дата блокировки", null=False, default=datetime.utcnow
    )
    date_unblocked = models.DateField(
        verbose_name="Дата разблокировки", null=True
    )

    def __str__(self):
        return f"{self.user}"


class UserRole(models.Model):
    """роль пользователя"""

    name = models.CharField(
        max_length=100, verbose_name="Название роли пользователя", null=False
    )

    def __str__(self):
        return f"{self.name}"


class GameAccount(models.Model):
    """Аккаунт пользователя на разных платформах"""

    nick_name = models.CharField(
        max_length=500,
        verbose_name="Ник пользователя на платформе",
        default="Ник",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        related_name="accounts",
        verbose_name="Пользователь",
        null=False,
        on_delete=models.CASCADE,
    )
    platform = models.ForeignKey(
        "Platform",
        related_name="accounts",
        verbose_name="Платфрома",
        null=False,
        on_delete=models.CASCADE,
    )
    platform_token = models.CharField(
        max_length=500,
        verbose_name="ID или токен пользователя",
        default="",
    )

    class Meta:
        unique_together = (('user', 'platform'),)

    def __str__(self):
        return f"{self.nick_name} {self.user} on {self.platform}"


class Platform(models.Model):
    """игровая платформа"""

    name = models.CharField(
        max_length=250, verbose_name="Название платформы", null=False
    )

    def __str__(self):
        return f"{self.name}"


class Notification(models.Model):
    MAILING = 1
    PERSONAL = 2
    STATUSES = ((MAILING, "mailing"), (PERSONAL, "personal"))
    text = models.CharField(
        max_length=5000, null=False, verbose_name="Текст уведомления"
    )
    type = models.IntegerField(choices=STATUSES, null=False, default=PERSONAL)
    date_created = models.DateTimeField(
        verbose_name="Дата создания уведомления",
        null=False,
        default=now,
    )
    educational_type_limit = models.ManyToManyField(
        "users.EducationalType",
        verbose_name="Рассылка по типу учебного заведения",
        blank=True,
    )
    location_limit = models.ManyToManyField(
        "users.Location",
        verbose_name="Рассылка по географическому расположению",
        blank=True,
    )
    federal_districts_limit = models.ManyToManyField(
        "users.FederalDistricts",
        verbose_name="Рассылка по географическому расположению "
                     "(федиральный округ)",
        blank=True,
    )
    games_limit = models.ManyToManyField(
        "games.Game",
        verbose_name="Рассылка по играм",
        blank=True,
    )
    confirmed_users = models.BooleanField(
        "Только для подтвержденных пользователей",
        default=False,
    )
    send = models.BooleanField(
        "Разослать",
        default=False,
    )
    endpoints = models.JSONField(
        verbose_name="Кнопки в уведомлении", blank=True, null=True
    )
    attachments = models.JSONField(
        verbose_name="Вложение", blank=True, null=True
    )
    system = models.BooleanField(
        verbose_name="Системное уведомление", default=False, null=False
    )

    def __repr__(self):
        return f"<Notification {self.text} type - {self.type}>"

    def __str__(self):
        return f"{self.text}"


class UserNotification(models.Model):
    NEW = 1
    SENDING = 2
    FAIL = 3
    DONE = 4
    STATUSES = (
        (NEW, "new"),
        (SENDING, "sending"),
        (FAIL, "fail"),
        (DONE, "done"),
    )

    user = models.ForeignKey(
        User, verbose_name="Пользователь", null=False, on_delete=models.CASCADE
    )
    notification = models.ForeignKey(
        Notification,
        verbose_name="Уведомление",
        null=False,
        on_delete=models.CASCADE,
    )
    status = models.IntegerField(choices=STATUSES, default=NEW)
    delivery_date = models.DateTimeField(
        verbose_name="Время доставки уведомления", default=now
    )

    def set_sending(self):
        self.status = UserNotification.SENDING
        self.save()
        return self

    def set_fail(self):
        self.status = UserNotification.FAIL
        self.save()
        return self

    def set_done(self):
        self.status = UserNotification.DONE
        self.save()
        return self

    class Meta:
        unique_together = (('notification', 'user'),)

    def __str__(self):
        return f"{self.user} тип - {self.status}"


@receiver(post_save, sender=UserNotification)
def create_task_user_notifications(instance, **kwargs):
    if instance.status in [UserNotification.NEW, UserNotification.FAIL]:
        data = {"id": instance.id}
        clock = ClockedSchedule.objects \
            .filter(clocked_time=instance.delivery_date).first()
        if not clock:
            clock = ClockedSchedule(clocked_time=instance.delivery_date)
            clock.save()
        periodic_task = PeriodicTask(
            task="users.tasks.send_user_notifications",
            name=f"send_user_notifications_{instance.id}_{uuid.uuid4()}",
            clocked=clock,
            enabled=True,
            one_off=True,
            kwargs=json.dumps(data),
        )
        periodic_task.save()


def get_selected_users(instance):
    users = User.objects.filter()
    if instance.educational_type_limit.exists():
        users = users.filter(
            educational_institution__type__in=instance.
                educational_type_limit.all()
        )
    if instance.location_limit.exists():
        users = users.filter(
            educational_institution__location__in= \
                instance.location_limit.all()
        )
    if instance.federal_districts_limit.exists():
        users = users.filter(
            educational_institution__location__federal_districts__in= \
                instance.federal_districts_limit.all()
        )
    if instance.games_limit.exists():
        users = users.filter(
            game_subscription__in=list(instance.games_limit.all())
        )
    if instance.confirmed_users:
        users = users.all()
        return [user for user in users if user.verified]

    return users.all()


@receiver(post_save, sender=Notification)
def event_notifications(instance, **kwargs):
    if (instance.type == Notification.MAILING) and instance.send:
        selected_users = get_selected_users(instance)
        for user in selected_users:
            notification = UserNotification(
                user=user,
                notification=instance,
                delivery_date=instance.date_created
            )
            notification.save()
        instance.send = False
        instance.save()
