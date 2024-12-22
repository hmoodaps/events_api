from rest_framework import status, viewsets, filters, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Guest, Reservation
from .models import Movie
from .serializer import GuestSerializer, MovieSerializer, ReservationSerializer


@api_view(['POST'])
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
@api_view(['GET'])
def get_movies(request):
    movies = Movie.objects.all()
    data = []
    for movie in movies:
        movie_data = {
            'id': movie.id,
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
            'rating': movie.rating,
            'imdb_rating': movie.imdb_rating,
            'tags': movie.tags,
        }
        data.append(movie_data)
    return Response(data)


class GuestViewSet(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']  # البحث حسب الحقول المتوفرة فقط
    authentication_classes = [TokenAuthentication]


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'name', 'release_date', 'duration',
        'rating', 'imdb_rating', 'tags', 'actors',
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
                "age": reservation.guest.id,
                "seats": reservation.guest.seats,
                "seat_price": reservation.guest.seat_price,
                "total_price": reservation.guest.total_price,
                "show_date": reservation.guest.show_date,
                "show_time": reservation.guest.show_time,
                "movie_id": reservation.guest.movie_id,
            },
            "movie": {
                "id": reservation.movie.id,
                "name": reservation.movie.name,
                "seats": reservation.movie.seats,
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
                "rating": reservation.movie.rating,
                "imdb_rating": reservation.movie.imdb_rating,
                "tags": reservation.movie.tags,
                "actors": reservation.movie.actors,
            }
        }
