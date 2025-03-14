from django.conf import settings
from django.contrib.auth.models import Group
from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Reservation, Showtime

from .models import Guest, Movie, generate_reservation_code
from .permissions import CanCreateReservationPermission
from .serializer import ReservationSerializer, MovieSerializer, GuestSerializer


class StripeKeys(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'secret_key': settings.STRIPE_SECRET_KEY,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  # التأكد من أن المستخدم مسجل دخوله
def create_superuser(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_superuser(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "User created successfully",
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_reservation(request):
    reservation_code = request.data.get('reservation_code')

    if not reservation_code:
        return Response({"error": "reservation_code is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reservation = Reservation.objects.get(reservations_code=reservation_code)
        reservation.delete()
        return Response({"message": "Reservation deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_guest(request):
    guest_id = request.data.get('id')

    if not guest_id:
        return Response({"error": "Guest id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # إنشاء مستخدم جديد للضيف (إذا كنت ترغب في ربطه بحساب)
        user, created = User.objects.get_or_create(username=guest_id)

        # إضافة الضيف إلى مجموعة "Guests" الخاصة بهم
        guests_group, _ = Group.objects.get_or_create(name='Guests')
        user.groups.add(guests_group)

        # إنشاء أو العثور على الضيف المرتبط بالمستخدم
        guest, created = Guest.objects.get_or_create(id=guest_id, user=user)

        # إنشاء التوكن للمستخدم (الضيف)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "id": guest.id,
            "token": token.key  # إرجاع التوكن الخاص بالضيف
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, CanCreateReservationPermission])
def create_reservation(request):
    guest_id = request.data.get('guest_id')
    movie_id = request.data.get('movie_id')
    showtime_id = request.data.get('showtime_id')  # إضافة showtime_id
    seat_numbers = request.data.get('seat_numbers') or request.data.get('seat_number')

    # التأكد من أن seat_numbers هو قائمة حتى لو تم إرسال مقعد واحد فقط
    if isinstance(seat_numbers, str):
        seat_numbers = [seat_numbers]

    if not guest_id or not movie_id or not showtime_id or not seat_numbers:
        return Response({"error": "guest_id, movie_id, showtime_id, and seat_numbers are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        guest = Guest.objects.get(id=guest_id)
        movie = Movie.objects.get(id=movie_id)
        showtime = Showtime.objects.get(id=showtime_id)

        # التحقق من أن الفيلم يتطابق مع العرض المحدد
        if showtime.movie != movie:
            return Response({"error": "The selected showtime does not match the movie."},
                            status=status.HTTP_400_BAD_REQUEST)

        # التحقق من عدم حجز المقاعد مسبقًا في العرض
        unavailable_seats = set(seat_numbers) & set(showtime.reserved_seats)
        if unavailable_seats:
            return Response({"error": f"Seats {list(unavailable_seats)} are already reserved"},
                            status=status.HTTP_400_BAD_REQUEST)

        # إضافة المقاعد الجديدة فقط إلى reserved_seats (بدون رمز الحجز)
        updated_seats = showtime.reserved_seats + seat_numbers
        showtime.reserved_seats = updated_seats
        showtime.available_seats = showtime.total_seats - len(showtime.reserved_seats)  # تحديث المقاعد المتاحة
        showtime.save()

        # إنشاء الحجز (من غير إضافة المقاعد إلى reserved_seats في الحجز)
        reservation = Reservation.objects.create(
            guest=guest, movie=movie, reservations_code=generate_reservation_code()
        )

        return Response({
            "reservation_code": reservation.reservations_code,
            "reserved_seats": seat_numbers  # عرض المقاعد المحجوزة فقط
        }, status=status.HTTP_201_CREATED)

    except Guest.DoesNotExist:
        return Response({"error": "Guest not found"}, status=status.HTTP_404_NOT_FOUND)
    except Movie.DoesNotExist:
        return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)
    except Showtime.DoesNotExist:
        return Response({"error": "Showtime not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_movies(request):
    movies = Movie.objects.all()
    data = []
    for movie in movies:
        show_times_data = []

        for showtime in movie.show_times.all():
            showtime_data = {
                'id': showtime.id,
                'date': showtime.date,
                'time': showtime.time,
                'hall': showtime.hall,
                'total_seats': showtime.total_seats,
                'available_seats': showtime.available_seats,
                'ticket_price': showtime.ticket_price,
                'reserved_seats': showtime.reserved_seats,
            }
            show_times_data.append(showtime_data)

        movie_data = {
            'id': movie.id,
            'added_date': movie.added_date,
            'name': movie.name,
            'show_times': show_times_data,  # هنا تم تحديثها لعرض تفاصيل العروض
            'photo': movie.photo,
            'vertical_photo': movie.vertical_photo,
            'description': movie.description,
            'short_description': movie.short_description,
            'sponsor_video': movie.sponsor_video,
            'actors': movie.actors,
            'release_date': movie.release_date,
            'duration': movie.duration,
            'imdb_rating': movie.imdb_rating,
            'tags': movie.tags,
        }
        data.append(movie_data)

    return Response(data)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name', 'release_date', 'duration', 'imdb_rating', 'tags', 'actors', 'show_times',
    ]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        movie = self.get_object()
        movie.delete()
        return Response({"message": "Movie and related reservations deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
