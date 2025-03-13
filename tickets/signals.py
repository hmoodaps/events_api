from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Movie, Reservation

@receiver(post_save, sender=Reservation)
def update_reserved_seats_on_create(sender, instance, created, **kwargs):
    if created:
        movie = instance.movie
        movie.reserved_seats.append(instance.reservations_code)
        movie.available_seats -= 1
        movie.reservations += 1
        movie.save()


@receiver(post_delete, sender=Reservation)
def update_reserved_seats_on_delete(sender, instance, **kwargs):
    movie = instance.movie
    if instance.reservations_code in movie.reserved_seats:
        movie.reserved_seats.remove(instance.reservations_code)
    movie.available_seats += 1
    movie.reservations -= 1
    movie.save()
