# Generated by Django 3.2.8 on 2022-07-07 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_alter_notification_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set(),
        ),
    ]
