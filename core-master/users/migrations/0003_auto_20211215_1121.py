# Generated by Django 3.2.8 on 2021-12-15 11:21

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_auto_20211215_0650"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="attachment",
        ),
        migrations.AddField(
            model_name="notification",
            name="attachment",
            field=models.JSONField(
                blank=True, null=True, verbose_name="Вложение"
            ),
        ),
        migrations.RemoveField(
            model_name="notification",
            name="endpoint",
        ),
        migrations.AddField(
            model_name="notification",
            name="endpoint",
            field=models.JSONField(
                blank=True, null=True, verbose_name="Кнопки в уведомлении"
            ),
        ),
        migrations.AlterField(
            model_name="usernotification",
            name="delivered",
            field=models.CharField(
                choices=[
                    ("new", "new"),
                    ("sending", "sending"),
                    ("fail", "fail"),
                    ("done", "done"),
                ],
                default="new",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="usernotification",
            name="delivery_date",
            field=models.DateTimeField(
                default=datetime.datetime(2021, 12, 15, 11, 21, 9, 216231),
                verbose_name="Время доставки уведомления",
            ),
        ),
    ]
