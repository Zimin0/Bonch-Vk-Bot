# Generated by Django 3.2.8 on 2022-07-10 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_alter_user_vk_id'),
        ('games', '0003_auto_20220531_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='platform',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.platform', verbose_name='Платформа игры'),
        ),
    ]
