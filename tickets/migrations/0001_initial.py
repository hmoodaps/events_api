# Generated by Django 5.1.4 on 2024-12-16 05:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('seats', models.JSONField(default=list)),
                ('seat_price', models.FloatField(default=0.0)),
                ('total_price', models.FloatField(default=0.0)),
                ('show_date', models.CharField(default='2024-01-01', max_length=20)),
                ('show_time', models.CharField(default='12:00 PM', max_length=20)),
                ('movie_id', models.IntegerField()),
                ('age', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('show_times', models.JSONField(default=dict)),
                ('seats', models.IntegerField(default=100)),
                ('available_seats', models.IntegerField(default=100)),
                ('reservations', models.IntegerField(blank=True, default=0)),
                ('photo', models.CharField(default='https://st2.depositphotos.com/1105977/9877/i/450/depositphotos_98775856-stock-photo-retro-film-production-accessories-still.jpg', max_length=255)),
                ('vertical_photo', models.CharField(blank=True, max_length=255)),
                ('ticket_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('reservedSeats', models.JSONField(blank=True, default=list)),
                ('description', models.TextField(blank=True)),
                ('short_description', models.TextField(blank=True, max_length=150)),
                ('sponsor_video', models.URLField(blank=True)),
                ('actors', models.JSONField(blank=True, default=list)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('duration', models.CharField(blank=True, max_length=50)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('imdb_rating', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('tags', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservations_code', models.CharField(blank=True, editable=False, max_length=4, unique=True)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations_set', to='tickets.guest')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations_set', to='tickets.movie')),
            ],
        ),
    ]
