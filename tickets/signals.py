from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Showtime, Reservation

@receiver(post_save, sender=Reservation)
def update_reserved_seats_on_create(sender, instance, created, **kwargs):
    if created:
        showtime = instance.showtime  # ✅ Correct way to fetch Showtime
        reserved_seats = instance.showtime.reserved_seats  # ✅ Fetch from Showtime

        # Update available seats count
        showtime.available_seats = showtime.total_seats - len(reserved_seats)

        showtime.save()

@receiver(post_delete, sender=Reservation)
def update_reserved_seats_on_delete(sender, instance, **kwargs):
    showtime = instance.showtime  # ✅ Fetch Showtime
    reserved_seats = showtime.reserved_seats  # ✅ Get reserved seats list

    # Ensure reservation seats are removed from the showtime
    if reserved_seats:
        for seat in reserved_seats:
            if seat in showtime.reserved_seats:
                showtime.reserved_seats.remove(seat)

        # Update available seats count
        showtime.available_seats = showtime.total_seats - len(showtime.reserved_seats)

        showtime.save()
