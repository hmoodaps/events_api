from rest_framework import serializers
from .models import Movie, Guest, Reservation

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'name', 'show_times', 'added_Date', 'seats', 'available_seats',
                  'reservations', 'photo', 'ticket_price', 'reservedSeats', 'description',
                  'short_description', 'vertical_photo', 'sponsor_video', 'actors', 'release_date',
                  'duration', 'imdb_rating', 'tags']  # إضافة باقي الحقول التي تود إبقائها

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id']  # فقط الـ id للضيف

class ReservationSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    guest = GuestSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'movie', 'guest', 'reservations_code']  # باقي الحقول التي تحتاجها

    def create(self, validated_data):
        movie_data = validated_data.pop('movie')
        guest_data = validated_data.pop('guest')

        # تحقق من وجود الفيلم في قاعدة البيانات باستخدام الـ id
        try:
            movie = Movie.objects.get(id=movie_data['id'])  # البحث باستخدام id فقط
        except Movie.DoesNotExist:
            raise serializers.ValidationError({"movie": "The specified movie does not exist."})

        # تحقق من وجود الضيف في قاعدة البيانات باستخدام الـ id
        try:
            guest = Guest.objects.get(id=guest_data['id'])  # البحث باستخدام id فقط
        except Guest.DoesNotExist:
            raise serializers.ValidationError({"guest": "The specified guest does not exist."})

        # إنشاء الحجز
        reservation = Reservation.objects.create(movie=movie, guest=guest, **validated_data)
        return reservation

    def update(self, instance, validated_data):
        # تحديث movie باستخدام id
        movie_data = validated_data.pop('movie', None)
        if movie_data:
            try:
                movie = Movie.objects.get(id=movie_data['id'])  # البحث باستخدام id فقط
                instance.movie = movie
            except Movie.DoesNotExist:
                raise serializers.ValidationError({"movie": "The specified movie does not exist."})

        # تحديث guest باستخدام id
        guest_data = validated_data.pop('guest', None)
        if guest_data:
            try:
                guest = Guest.objects.get(id=guest_data['id'])  # البحث باستخدام id فقط
                instance.guest = guest
            except Guest.DoesNotExist:
                raise serializers.ValidationError({"guest": "The specified guest does not exist."})

        # تحديث الحجز
        return super().update(instance, validated_data)
