from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reservation, Movie

# تحديث المعلومات عند إضافة حجز
@receiver(post_save, sender=Reservation)
def update_movie_reservations_on_save(sender, instance, created, **kwargs):
    movie = instance.movie

    # تحقق إذا كان الحجز جديدًا
    if created:
        movie.reservations += 1
        # إضافة المقاعد المحجوزة بناءً على الحجز
        movie.reservedSeats = list(set(movie.reservedSeats + instance.guest.seats))

    # تحديث المقاعد المتاحة
    movie.available_seats = movie.seats - len(movie.reservedSeats)

    print(f"Reservations updated: {movie.reservations}")
    print(f"Reserved Seats updated: {movie.reservedSeats}")
    print(f"Available Seats updated: {movie.available_seats}")

    # حفظ التعديلات في الفيلم
    movie.save()


# تحديث المعلومات عند حذف حجز
@receiver(post_delete, sender=Reservation)
def update_movie_reservations_on_delete(sender, instance, **kwargs):
    movie = instance.movie

    # تحديث عدد الحجوزات بعد الحذف
    movie.reservations = Reservation.objects.filter(movie=movie).count()

    # إزالة المقاعد المحجوزة من reservedSeats بناءً على الـ guest's seat ID
    # سيتم الآن إزالة المقاعد المحجوزة باستخدام ID الضيف وليس المقاعد الفعلية
    movie.reservedSeats = [seat for seat in movie.reservedSeats if seat not in instance.guest.seats]

    # تحديث المقاعد المتاحة
    movie.available_seats = movie.seats - len(movie.reservedSeats)

    print(f"Reservations updated: {movie.reservations}")
    print(f"Reserved Seats updated: {movie.reservedSeats}")
    print(f"Available Seats updated: {movie.available_seats}")

    # حفظ التعديلات في الفيلم
    movie.save()
