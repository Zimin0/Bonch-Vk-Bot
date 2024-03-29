# Generated by Django 3.2.8 on 2022-12-18 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0038_rename_csgomaps_csgomap'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsgoPeakStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected', models.BooleanField(verbose_name='пикнули/забанили')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.csgomap', verbose_name='карта')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournaments.match', verbose_name='матч')),
            ],
        ),
    ]
