# Generated by Django 3.2.8 on 2022-07-09 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0032_auto_20220709_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='type',
            field=models.IntegerField(choices=[(3, 'Верхняя сетка'), (2, 'Нижняя сетка')], default=3, verbose_name='тип'),
        ),
    ]
