# Generated by Django 3.2.8 on 2022-05-10 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_userverificationrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='userverificationrequest',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Архивирована'),
        ),
    ]