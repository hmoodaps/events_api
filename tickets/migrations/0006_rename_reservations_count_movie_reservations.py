# Generated by Django 5.1.1 on 2024-09-17 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_rename_reservations_guest_reservations_count_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='reservations',
            new_name='reservations',
        ),
    ]