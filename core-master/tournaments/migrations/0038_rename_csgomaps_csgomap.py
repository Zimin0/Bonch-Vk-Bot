# Generated by Django 3.2.8 on 2022-12-18 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0037_alter_csgomaps_server_command'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CsGoMaps',
            new_name='CsgoMap',
        ),
    ]