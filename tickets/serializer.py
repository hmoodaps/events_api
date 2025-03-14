from rest_framework import serializers

from .models import Guest, Reservation
from .models import Movie, Showtime


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['date', 'time', 'hall', 'total_seats', 'available_seats', 'ticket_price', 'reserved_seats']

class MovieSerializer(serializers.ModelSerializer):
    show_times = ShowtimeSerializer(many=True)  # السماح بإرسال أوقات العرض مع الفيلم

    class Meta:
        model = Movie
        fields = [
            'id', 'name', 'photo', 'vertical_photo', 'description', 'short_description',
            'sponsor_video', 'actors', 'release_date', 'added_date', 'duration',
            'imdb_rating', 'tags', 'show_times'
        ]

    def create(self, validated_data):
        """إنشاء فيلم مع أوقات العرض"""
        show_times_data = validated_data.pop('show_times', [])  # استخراج أوقات العرض من البيانات
        movie = Movie.objects.create(**validated_data)

        for showtime_data in show_times_data:
            Showtime.objects.create(movie=movie, **showtime_data)  # إنشاء أوقات العرض وربطها بالفيلم

        return movie


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id']


class ReservationSerializer(serializers.ModelSerializer):
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all())
    guest = serializers.PrimaryKeyRelatedField(queryset=Guest.objects.all())

    class Meta:
        model = Reservation
        fields = ['id', 'movie', 'guest', 'reservations_code']

    def create(self, validated_data):
        """إنشاء حجز جديد باستخدام ID فقط دون الحاجة لجلب الكائنات يدويًا."""
        return Reservation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """تحديث بيانات الحجز."""
        instance.movie = validated_data.get('movie', instance.movie)
        instance.guest = validated_data.get('guest', instance.guest)
        instance.save()
        return instance
