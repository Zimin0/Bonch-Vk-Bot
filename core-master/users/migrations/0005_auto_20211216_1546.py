# Generated by Django 3.2.8 on 2021-12-16 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_usernotification_delivery_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notification",
            old_name="attachment",
            new_name="attachments",
        ),
        migrations.RenameField(
            model_name="notification",
            old_name="endpoint",
            new_name="endpoints",
        ),
    ]