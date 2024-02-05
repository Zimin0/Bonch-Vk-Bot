# Generated by Django 3.2.8 on 2022-01-27 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0012_alter_tournamentevent_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match",
            name="next_match",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="previous_match",
                to="tournaments.match",
                verbose_name="Следующий матч",
            ),
        ),
    ]