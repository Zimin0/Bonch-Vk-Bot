# Generated by Django 3.2.8 on 2022-01-27 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_auto_20211218_1340"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.IntegerField(
                choices=[(1, "mailing"), (2, "personal")]
            ),
        ),
    ]
