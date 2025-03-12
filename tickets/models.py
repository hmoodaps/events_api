from django.db import models
import random
import string

from django.db import models

class Movie(models.Model):
    name = models.CharField(max_length=100)
    show_times = models.JSONField(default=dict)  # JSON متوافقة مع ShowTimesResponse
    seats = models.IntegerField(default=100)  # int?
    available_seats = models.IntegerField(default=100)  # int?
    reservations = models.IntegerField(default=0, blank=True)  # int?
    photo = models.CharField(
        max_length=255,
        default="https://st2.depositphotos.com/1105977/9877/i/450/depositphotos_98775856-stock-photo-retro-film-production-accessories-still.jpg"
    )  # String?
    vertical_photo = models.CharField(max_length=255, blank=True)  # String?
    ticket_price = models.FloatField()  # double?
    reservedSeats = models.JSONField(default=list, blank=True)  # List<dynamic>?
    description = models.TextField(blank=True)  # String?
    short_description = models.TextField(max_length=150, blank=True)  # String?
    sponsor_video = models.URLField(blank=True)  # String?
    actors = models.JSONField(default=list, blank=True)  # List<dynamic>?
    release_date = models.DateField(blank=True, null=True)  # String? (بتنسيق التاريخ مثل yyyy-MM-dd)
    added_Date = models.DateField(blank=True, null=True)  # String? (بتنسيق التاريخ مثل yyyy-MM-dd)
    duration = models.CharField(max_length=50, blank=True)  # String?
    imdb_rating = models.FloatField(blank=True, null=True)  # double?
    tags = models.JSONField(default=list, blank=True)  # List<dynamic>?


    def __str__(self):
        return self.name


class Guest(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # المفتاح الأساسي
    def __str__(self):
        return self.id





class Reservation(models.Model):
    movie = models.ForeignKey('Movie', related_name='reservations_set', on_delete=models.CASCADE)
    guest = models.ForeignKey('Guest', related_name='reservations_set', on_delete=models.CASCADE)
    reservations_code = models.CharField(max_length=4, unique=True, blank=True, editable=False)

    # احفظ الحجز مع قيمة معرف الضيف والفيلم

def generate_reservation_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(4))
