# Generated by Django 3.2.8 on 2022-06-04 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_location_federal_districts'),
        ('tournaments', '0016_auto_20220531_0004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='referee',
        ),
        migrations.AddField(
            model_name='tournament',
            name='referee',
            field=models.ManyToManyField(blank=True, null=True, related_name='tournament_referee', to='users.User', verbose_name='Судья туринира'),
        ),
    ]