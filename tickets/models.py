import jsonfield
from django.contrib.auth.models import Group
from django.db import models
import random
import string

from rest_framework.authtoken.admin import User



def default_empty_list():
    return []


class Movie(models.Model):
    name = models.CharField(max_length=100)
    photo = models.CharField(
        max_length=255,
        default="https://st2.depositphotos.com/1105977/9877/i/450/depositphotos_98775856-stock-photo-retro-film-production-accessories-still.jpg"
    )
    vertical_photo = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(max_length=150, blank=True, null=True)
    sponsor_video = models.URLField(blank=True, null=True)
    actors = models.JSONField(default=default_empty_list, blank=True)
    release_date = models.DateField(blank=True, null=True)
    added_date = models.DateField(auto_now_add=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    imdb_rating = models.FloatField(blank=True, null=True)
    tags = models.JSONField(default=default_empty_list, blank=True)

    def __str__(self):
        return self.name


class Showtime(models.Model):
    """ موديل يمثل عرضًا معينًا للفيلم في يوم محدد وقاعة معينة """
    movie = models.ForeignKey(Movie, related_name="show_times", on_delete=models.CASCADE)
    date = models.DateField()  # تاريخ العرض
    time = models.TimeField()  # وقت العرض
    hall = models.CharField(max_length=50)  # القاعة
    total_seats = models.IntegerField(default=100)  # عدد المقاعد الكلي
    available_seats = models.IntegerField(default=100)  # عدد المقاعد المتاحة
    ticket_price = models.FloatField()  # سعر التذكرة
    reserved_seats = models.JSONField(default=default_empty_list, blank=True)  # قائمة المقاعد المحجوزة

    class Meta:
        unique_together = ('movie', 'date', 'time', 'hall')  # منع التكرار لنفس الفيلم في نفس القاعة والتوقيت

    def __str__(self):
        return f"{self.movie.name} - {self.date} at {self.time} in {self.hall}"


class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return f"Guest {self.id}"

    def save(self, *args, **kwargs):
        """عند إنشاء ضيف جديد، تأكد من إنشاء مستخدم فريد له وإضافته إلى مجموعة الضيوف."""
        if not self.user:  # إذا لم يكن هناك مستخدم مرتبط بالضيف، أنشئه
            user, created = User.objects.get_or_create(username=self.id)  # استخدام الـ id الخاص بالضيف كاسم مستخدم
            self.user = user  # ربط الـ User بالضيف

        super().save(*args, **kwargs)  # حفظ الضيف

        # إضافة الضيف إلى مجموعة "Guests"
        guests_group, _ = Group.objects.get_or_create(name='Guests')
        self.user.groups.add(guests_group)  # إضافة الـ User إلى مجموعة الضيوف


def generate_reservation_code():
    """توليد كود حجز عشوائي مكون من 6 أحرف وأرقام."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=6))


class Reservation(models.Model):
    movie = models.ForeignKey(Movie, related_name='movie_reservations', on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, related_name='guest_reservations', on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, related_name='reservations', on_delete=models.CASCADE)  # إضافة حقل showtime
    reservations_code = models.CharField(max_length=6, unique=True, blank=True, editable=False)
    reserved_seats = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        if not self.reservations_code:
            while True:
                code = generate_reservation_code()
                if not Reservation.objects.filter(reservations_code=code).exists():
                    self.reservations_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.reservations_code} | Movie: {self.movie.name} | Guest ID: {self.guest.id}"

# models.py
class MolliePayment(models.Model):
    mollie_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    details = jsonfield.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mollie_id} - {self.status}"