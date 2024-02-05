# Generated by Django 3.2.8 on 2021-12-09 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0007_tournament_winner"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tournamentevent",
            name="time",
        ),
        migrations.AddField(
            model_name="tournamentevent",
            name="time_end",
            field=models.DateTimeField(
                null=True, verbose_name="Время завершения"
            ),
        ),
        migrations.AddField(
            model_name="tournamentevent",
            name="time_start",
            field=models.DateTimeField(null=True, verbose_name="Время начала"),
        ),
    ]
