from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Movie, Reservation

@receiver(post_save, sender=Reservation)
def update_reserved_seats_on_create(sender, instance, created, **kwargs):
    if created:
        movie = instance.movie
        movie.available_seats -= len(instance.movie.reserved_seats)  # خصم عدد المقاعد المحجوزة فقط
        movie.reservations += 1
        movie.save()


@receiver(post_delete, sender=Reservation)
def update_reserved_seats_on_delete(sender, instance, **kwargs):
    movie = instance.movie
    for seat in instance.reserved_seats:  # ✅ إزالة المقاعد المحجوزة من الفيلم
        if seat in movie.reserved_seats:
            movie.reserved_seats.remove(seat)

    movie.available_seats += len(instance.reserved_seats)  # ✅ إعادة المقاعد المتاحة
    movie.reservations -= 1
    movie.save()
