# Generated by Django 3.2.8 on 2022-12-18 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0035_alter_csgoround_round_map'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsGoMaps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='название карты')),
                ('server_command', models.IntegerField(max_length=100, verbose_name='команда для сервера')),
            ],
        ),
        migrations.AlterField(
            model_name='csgoround',
            name='round_map',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tournaments.csgomaps', verbose_name='карта раунда'),
        ),
    ]
