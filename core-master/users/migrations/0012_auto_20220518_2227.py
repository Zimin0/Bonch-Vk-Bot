# Generated by Django 3.2.8 on 2022-05-18 19:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_userverificationrequest_archived'),
    ]

    operations = [
        migrations.CreateModel(
            name='FederalDistricts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название населенного пункта')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='date_next_verification',
            field=models.DateField(default=datetime.date.today, verbose_name='дата следующей верификации'),
        ),
        migrations.AddField(
            model_name='location',
            name='federal_districts',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='federation_subjects', to='users.federaldistricts', verbose_name='Федеральный округ'),
        ),
    ]
