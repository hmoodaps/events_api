# Generated by Django 5.1.1 on 2024-09-15 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_guest_seats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='seats',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='movie',
            name='reservations',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='movie',
            name='reservedSeats',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
