# Generated by Django 3.2.8 on 2021-12-16 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_auto_20211216_1546"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Attachment",
        ),
        migrations.DeleteModel(
            name="Endpoint",
        ),
    ]
