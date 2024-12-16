from django.db import models
import random
import string

from django.db import models

class Movie(models.Model):
    name = models.CharField(max_length=100)
    show_times = models.JSONField(default=dict)
    seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    reservations = models.IntegerField(default=0, blank=True)
    photo = models.CharField(max_length=255, default="https://st2.depositphotos.com/1105977/9877/i/450/depositphotos_98775856-stock-photo-retro-film-production-accessories-still.jpg")
    vertical_photo = models.CharField(max_length=255, blank=True)
    ticket_price = models.DecimalField(max_digits=5, decimal_places=2)
    reservedSeats = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=150, blank=True)
    sponsor_video = models.URLField(blank=True)
    actors = models.JSONField(default=list, blank=True)
    release_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name


class Guest(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # المفتاح الأساسي
    seats = models.JSONField(default=list)  # مصفوفة
    seat_price = models.FloatField(default=0.0)  # سعر المقعد
    total_price = models.FloatField(default=0.0)  # السعر الكلي
    show_date = models.CharField(max_length=20, default="2024-01-01")  # تاريخ العرض
    show_time = models.CharField(max_length=20, default="12:00 PM")  # وقت العرض
    movie_id = models.IntegerField()  # معرف الفيلم
    age = models.IntegerField()




class Reservation(models.Model):
    movie = models.ForeignKey('Movie', related_name='reservations_set', on_delete=models.CASCADE)
    guest = models.ForeignKey('Guest', related_name='reservations_set', on_delete=models.CASCADE)
    reservations_code = models.CharField(max_length=4, unique=True, blank=True, editable=False)

    # احفظ الحجز مع قيمة معرف الضيف والفيلم

def generate_reservation_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(4))
