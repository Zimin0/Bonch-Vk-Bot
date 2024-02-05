# Generated by Django 3.2.8 on 2022-07-01 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_remove_usereducation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='confirmed_users',
            field=models.BooleanField(default=False, verbose_name='Только подтвержденные учетные записи'),
        ),
        migrations.AddField(
            model_name='notification',
            name='educational_type_limit',
            field=models.ManyToManyField(blank=True, to='users.EducationalType', verbose_name='Ограничение по типу учебного заведения'),
        ),
        migrations.AddField(
            model_name='notification',
            name='federal_districts_limit',
            field=models.ManyToManyField(blank=True, to='users.FederalDistricts', verbose_name='Ограничение по географическому расположению (федиральный округ)'),
        ),
        migrations.AddField(
            model_name='notification',
            name='location_limit',
            field=models.ManyToManyField(blank=True, to='users.Location', verbose_name='Ограничение по географическому расположению'),
        ),
    ]
