from rest_framework import serializers

from .models import Guest, Reservation
from .models import Movie, Showtime


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['id', 'date', 'time', 'hall', 'total_seats', 'available_seats', 'ticket_price', 'reserved_seats']


class MovieSerializer(serializers.ModelSerializer):
    # استدعاء الـ ShowtimeSerializer لتضمين تفاصيل الشو تايم
    show_times = ShowtimeSerializer(many=True, read_only=True)  # عرض تفاصيل الشو تايم (العروض المرتبطة بالفيلم)

    class Meta:
        model = Movie
        fields = [
            'id',
            'name',
            'show_times',  # تضمين العروض المرتبطة بالفيلم
            'photo',
            'vertical_photo',
            'description',
            'short_description',
            'sponsor_video',
            'actors',
            'release_date',
            'added_date',
            'duration',
            'imdb_rating',
            'tags'
        ]


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
