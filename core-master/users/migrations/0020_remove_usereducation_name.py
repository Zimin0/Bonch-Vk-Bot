# Generated by Django 3.2.8 on 2022-06-16 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_alter_user_registration_sate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usereducation',
            name='name',
        ),
    ]
