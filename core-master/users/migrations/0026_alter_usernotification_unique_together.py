# Generated by Django 3.2.8 on 2022-07-05 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_alter_usernotification_notification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usernotification',
            unique_together={('notification', 'user')},
        ),
    ]
