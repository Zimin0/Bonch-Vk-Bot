# Generated by Django 3.2.8 on 2021-12-07 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="single",
            field=models.BooleanField(default=False, verbose_name="Одиночная"),
        ),
    ]
