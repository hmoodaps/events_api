from django.contrib.auth.models import Group
from django.db import models
import random
import string

from rest_framework.authtoken.admin import User


# الدالة لتعريف القيم الافتراضية
def default_empty_list():
    return []

class Movie(models.Model):
    name = models.CharField(max_length=100)
    show_times = models.JSONField(default=dict)
    seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    reservations = models.IntegerField(default=0, blank=True)
    photo = models.CharField(
        max_length=255,
        default="https://st2.depositphotos.com/1105977/9877/i/450/depositphotos_98775856-stock-photo-retro-film-production-accessories-still.jpg"
    )
    vertical_photo = models.CharField(max_length=255, blank=True, null=True)
    ticket_price = models.FloatField()
    # reserved_seats = models.JSONField(default=default_empty_list, blank=True)  # تعديل من lambda إلى دالة ثابتة
    description = models.TextField(blank=True, null=True)  # دعم القيم الفارغة
    short_description = models.TextField(max_length=150, blank=True, null=True)
    sponsor_video = models.URLField(blank=True, null=True)
    actors = models.JSONField(default=default_empty_list, blank=True)  # تعديل من lambda إلى دالة ثابتة
    release_date = models.DateField(blank=True, null=True)
    added_date = models.DateField(auto_now_add=True)  # تعيينه تلقائيًا عند الإضافة
    duration = models.CharField(max_length=50, blank=True, null=True)
    imdb_rating = models.FloatField(blank=True, null=True)
    tags = models.JSONField(default=default_empty_list, blank=True)  # تعديل من lambda إلى دالة ثابتة

    def __str__(self):
        return self.name


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
    movie = models.ForeignKey(Movie, related_name='movie_reservations', on_delete=models.CASCADE)  # تغيير الـ related_name هنا
    guest = models.ForeignKey(Guest, related_name='guest_reservations', on_delete=models.CASCADE)  # تغيير الـ related_name هنا
    reservations_code = models.CharField(max_length=6, unique=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        """ضمان أن كود الحجز فريد، مع محاولات غير محدودة حتى نحصل على كود غير مكرر."""
        if not self.reservations_code:
            while True:
                code = generate_reservation_code()
                if not Reservation.objects.filter(reservations_code=code).exists():
                    self.reservations_code = code
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation {self.reservations_code} | Movie: {self.movie.name} | Guest ID: {self.guest.id}"
