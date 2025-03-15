from rest_framework import serializers

from .models import Guest, Reservation
from .models import Movie, Showtime


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['id', 'date', 'time', 'hall', 'total_seats', 'available_seats', 'ticket_price', 'reserved_seats']

class MovieSerializer(serializers.ModelSerializer):
    show_times = ShowtimeSerializer(many=True, read_only=True)  # السماح بإرسال أوقات العرض مع الفيلم

    class Meta:
        model = Movie
        fields = [
            'id', 'name', 'photo', 'vertical_photo', 'description', 'short_description',
            'sponsor_video', 'actors', 'release_date', 'added_date', 'duration',
            'imdb_rating', 'tags', 'show_times'
        ]

    def create(self, validated_data):
        """إنشاء فيلم مع أوقات العرض"""
        show_times_data = self.context['request'].data.get('show_times', [])  # استخراج أوقات العرض من البيانات
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
    showtime = serializers.PrimaryKeyRelatedField(queryset=Showtime.objects.all())  # إضافة العرض

    reserved_seats = serializers.SerializerMethodField()  # حقل مخصص لجلب المقاعد المحجوزة

    class Meta:
        model = Reservation
        fields = ['id', 'movie', 'guest', 'showtime', 'reservations_code', 'reserved_seats']  # إضافة showtime

    def get_reserved_seats(self, obj):
        """إرجاع المقاعد المحجوزة من Showtime المرتبط بالحجز"""
        return obj.showtime.reserved_seats if obj.showtime else []
