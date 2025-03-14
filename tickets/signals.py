from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Showtime, Reservation

@receiver(post_save, sender=Reservation)
def update_reserved_seats_on_create(sender, instance, created, **kwargs):
    if created:
        # الحصول على الـ Showtime المرتبط بالحجز
        showtime = instance.movie.showtimes.get(id=instance.showtime.id)  # تأكد من أن لديك خاصية `showtime` في الحجز
        # خصم المقاعد المحجوزة
        showtime.available_seats -= len(instance.reserved_seats)
        showtime.reserved_seats.extend(instance.reserved_seats)  # إضافة المقاعد المحجوزة إلى قائمة المقاعد المحجوزة
        showtime.save()


@receiver(post_delete, sender=Reservation)
def update_reserved_seats_on_delete(sender, instance, **kwargs):
    # الحصول على الـ Showtime المرتبط بالحجز
    showtime = instance.movie.showtimes.get(id=instance.showtime.id)  # تأكد من أن لديك خاصية `showtime` في الحجز
    # إزالة المقاعد المحجوزة
    for seat in instance.reserved_seats:
        if seat in showtime.reserved_seats:
            showtime.reserved_seats.remove(seat)
    # إعادة المقاعد المتاحة
    showtime.available_seats += len(instance.reserved_seats)
    showtime.save()
