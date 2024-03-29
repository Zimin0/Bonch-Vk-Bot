# Generated by Django 3.2.8 on 2022-07-11 18:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0032_alter_gameaccount_nick_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания уведомления'),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='delivery_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Время доставки уведомления'),
        ),
    ]
