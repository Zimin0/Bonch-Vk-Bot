# Generated by Django 3.2.8 on 2022-06-14 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0007_teaminvites_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teaminvites',
            name='type',
            field=models.IntegerField(choices=[(1, 'новое'), (2, 'просмотренное')], default=1),
        ),
    ]
