from django.conf import settings
from rest_framework import status, viewsets, filters, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Guest, Reservation, Movie
from .serializer import MovieSerializer, ReservationSerializer

class StripeKeys(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'secret_key': settings.STRIPE_SECRET_KEY,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])  # إضافة المصادقة بواسطة التوكن
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



@api_view(['POST'])
def create_guest(request):
    # نأخذ فقط الـ id في الطلب
    guest_id = request.data.get('id')

    if not guest_id:
        return Response({"error": "Guest id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # إنشاء الضيف بناءً على id فقط
    try:
        guest = Guest.objects.create(id=guest_id)
        guest.save()

        return Response({
            "id": guest.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_movies(request):
    movies = Movie.objects.all()
    data = []
    for movie in movies:
        movie_data = {
            'id': movie.id,
            'added_Date':movie.added_Date,
            'name': movie.name,
            'show_times': movie.show_times,
            'seats': movie.seats,
            'available_seats': movie.available_seats,
            'reservations': movie.reservations,
            'photo': movie.photo,
            'vertical_photo': movie.vertical_photo,
            'ticket_price': movie.ticket_price,
            'reservedSeats': movie.reservedSeats,
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




class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name', 'release_date', 'duration',
         'imdb_rating', 'tags', 'actors','show_times',
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['reservations_code','movie__name', 'movie__actors', 'movie__tags']

    @action(detail=False, methods=['get'], url_path='search-by-seat')
    def search_by_seat(self, request):
        seat_number = request.query_params.get('seat')
        if not seat_number:
            return Response({"detail": "Seat number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = Reservation.objects.filter(guest__seats__contains=[seat_number]).first()

            if reservation:
                response_data = self.get_reservation_response_data(reservation)
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No reservation found for this seat"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        reservation_code = kwargs.get('pk')

        try:
            reservation = Reservation.objects.get(reservations_code=reservation_code)
            response_data = self.get_reservation_response_data(reservation)
            return Response(response_data, status=status.HTTP_200_OK)

        except Reservation.DoesNotExist:
            return Response({"detail": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_reservation_response_data(reservation):
        return {
            "reservation_code": reservation.reservations_code,
            "guest": {
                "id": reservation.guest.id,
            },
            "movie": {
                "id": reservation.movie.id,
                "name": reservation.movie.name,
                "seats": reservation.movie.seats,
                'added_Date': reservation.movie.added_date,
                "available_seats": reservation.movie.available_seats,
                "reservations": reservation.movie.reservations,
                "photo": reservation.movie.photo,
                "ticket_price": reservation.movie.ticket_price,
                "reservedSeats": reservation.movie.reservedSeats,
                "description": reservation.movie.description,
                "vertical_photo": reservation.movie.vertical_photo,
                "sponsor_video": reservation.movie.sponsor_video,
                "release_date": reservation.movie.release_date,
                "duration": reservation.movie.duration,
                "imdb_rating": reservation.movie.imdb_rating,
                "tags": reservation.movie.tags,
                "actors": reservation.movie.actors,
            }
        }
