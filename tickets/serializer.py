from rest_framework import serializers
from .models import Movie, Guest, Reservation

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'name', 'show_times', 'seats', 'available_seats', 'reservations', 'photo', 'vertical_photo', 'ticket_price', 'reserved_seats', 'description', 'short_description', 'sponsor_video', 'actors', 'release_date', 'added_date', 'duration', 'imdb_rating', 'tags']


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
