from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Showtime, Reservation

@receiver(post_save, sender=Reservation)
def update_reserved_seats_on_create(sender, instance, created, **kwargs):
    if created:
        showtime = instance.showtime  # ✅ الطريقة الصحيحة لجلب العرض مباشرة
        showtime.available_seats -= len(instance.reserved_seats)
        showtime.reserved_seats.extend(instance.reserved_seats)
        showtime.save()

@receiver(post_delete, sender=Reservation)
def update_reserved_seats_on_delete(sender, instance, **kwargs):
    showtime = instance.showtime  # ✅ استخدام instance مباشرة
    for seat in instance.reserved_seats:
        if seat in showtime.reserved_seats:
            showtime.reserved_seats.remove(seat)
    showtime.available_seats += len(instance.reserved_seats)
    showtime.save()
