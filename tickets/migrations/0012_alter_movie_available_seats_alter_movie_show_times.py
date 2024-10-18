# Generated by Django 5.1.2 on 2024-10-18 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0011_alter_movie_short_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='available_seats',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='movie',
            name='show_times',
            field=models.JSONField(default=dict),
        ),
    ]
