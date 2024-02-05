# Generated by Django 3.2.8 on 2022-12-18 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0040_csgopeakstage_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csgopeakstage',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='peak_stage', to='tournaments.match', verbose_name='матч'),
        ),
    ]
