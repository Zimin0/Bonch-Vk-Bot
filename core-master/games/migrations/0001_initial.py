# Generated by Django 3.2.8 on 2021-10-07 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=250, verbose_name="Название игры"
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=1000,
                        null=True,
                        verbose_name="Описание игры",
                    ),
                ),
                (
                    "platform",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.platform",
                        verbose_name="Платформа игры",
                    ),
                ),
            ],
        ),
    ]