# Generated by Django 3.2.8 on 2022-12-18 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0036_auto_20221218_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csgomaps',
            name='server_command',
            field=models.CharField(max_length=100, verbose_name='команда для сервера'),
        ),
    ]
