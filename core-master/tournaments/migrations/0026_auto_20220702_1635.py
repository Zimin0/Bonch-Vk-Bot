# Generated by Django 3.2.8 on 2022-07-02 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0025_tournament_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentevent',
            name='send_notification',
            field=models.BooleanField(default=False, verbose_name='Разослать уведомления'),
        ),
        migrations.AlterField(
            model_name='tournamentnotification',
            name='users_status',
            field=models.IntegerField(choices=[(1, 'Зарегестрированным'), (2, 'Играющим'), (3, 'Не рассылать')], default=3, verbose_name='Кому'),
        ),
    ]
