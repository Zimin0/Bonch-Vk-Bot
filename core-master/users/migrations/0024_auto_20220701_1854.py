# Generated by Django 3.2.8 on 2022-07-01 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20220701_1843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='changeable',
        ),
        migrations.AddField(
            model_name='notification',
            name='system',
            field=models.BooleanField(default=False, verbose_name='Системное уведомление'),
        ),
    ]
