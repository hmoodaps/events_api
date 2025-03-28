import hashlib
import hmac
import json

from django.conf import settings
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from mollie.api.client import Client
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Guest, Movie, generate_reservation_code, MolliePayment
from .models import Reservation, Showtime
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
@permission_classes([IsAuthenticated])
def create_reservation(request):
    guest_id = request.data.get('guest_id')
    movie_id = request.data.get('movie_id')
    showtime_id = request.data.get('showtime_id')
    seat_numbers = request.data.get('seat_numbers') or request.data.get('seat_number')

    if isinstance(seat_numbers, str):
        seat_numbers = [seat_numbers]

    if not guest_id or not movie_id or not showtime_id or not seat_numbers:
        return Response({"error": "guest_id, movie_id, showtime_id, and seat_numbers are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        guest = Guest.objects.get(id=guest_id)
        movie = Movie.objects.get(id=movie_id)
        showtime = Showtime.objects.get(id=showtime_id)

        if showtime.movie != movie:
            return Response({"error": "The selected showtime does not match the movie."},
                            status=status.HTTP_400_BAD_REQUEST)

        unavailable_seats = set(seat_numbers) & set(showtime.reserved_seats)
        if unavailable_seats:
            return Response({"error": f"Seats {list(unavailable_seats)} are already reserved"},
                            status=status.HTTP_400_BAD_REQUEST)

        updated_seats = showtime.reserved_seats + seat_numbers
        showtime.reserved_seats = updated_seats
        showtime.available_seats = showtime.total_seats - len(showtime.reserved_seats)
        showtime.save()

        reservation = Reservation.objects.create(
            guest=guest,
            movie=movie,
            showtime=showtime,
            reservations_code=generate_reservation_code()
        )

        return Response({
            "id": reservation.id,
            "reservation_code": reservation.reservations_code,
            "guest": guest.id,
            "movie": movie.name,
            "showtime": {
                "id": showtime.id,
                "date": showtime.date,
                "time": showtime.time,
                "hall": showtime.hall
            },
            "reserved_seats": seat_numbers
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
def get_reservation_by_code(request):
    reservation_code = request.query_params.get('reservation_code')

    if not reservation_code:
        return Response({"error": "reservation_code is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reservation = Reservation.objects.get(reservations_code=reservation_code)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_movies(request):
    movies = Movie.objects.prefetch_related("show_times").all()  # تحسين أداء الاستعلام
    serializer = MovieSerializer(movies, many=True)  # استخدام السيريالايزر مباشرة
    return Response(serializer.data, status=status.HTTP_200_OK)

#
# @api_view(['POST'])
# def create_movie(request):
#     """إضافة فيلم جديد مع أوقات العرض"""
#     serializer = MovieSerializer(data=request.data, context={'request': request})
#
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
def create_mollie_payment(request):
    mollie_client = Client()
    mollie_client.set_api_key(settings.MOLLIE_API_KEY)

    payment = mollie_client.payments.create({
        'amount': {
            'currency': 'EUR',
            'value': f"{request.data['amount']:.2f}"
        },
        'description': request.data.get('description', ''),
        'redirectUrl': request.data.get('redirectUrl', ''),
        'webhookUrl': request.data.get('webhookUrl', ''),
        'metadata': request.data.get('metadata', {})
    })

    MolliePayment.objects.create(
        mollie_id=payment.id,
        amount=request.data['amount'],
        status=payment.status,
        details=json.dumps(payment)  # ⭐ حفظ كل التفاصيل كـ JSON
    )

    return Response(payment)  # ⚡ يعيد كل البيانات كما هي من Mollie




def verify_mollie_webhook(request):
    webhook_secret = settings.MOLLIE_WEBHOOK_SECRET  # ⚠️ احفظه في settings.py
    received_sig = request.headers.get('Mollie-Signature')
    calculated_sig = hmac.new(
        webhook_secret.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    return received_sig == calculated_sig



@csrf_exempt
@api_view(['POST'])
def mollie_webhook(request):
    if not verify_mollie_webhook(request):
        return HttpResponse('Invalid signature', status=403)
    try:
        payment_id = request.data.get('id')
        mollie_client = Client()
        mollie_client.set_api_key(settings.MOLLIE_API_KEY)

        # جلب أحدث حالة للدفع من Mollie مباشرة
        payment = mollie_client.payments.get(payment_id)

        # تحديث قاعدة البيانات
        db_payment = MolliePayment.objects.get(mollie_id=payment_id)
        db_payment.status = payment.status
        db_payment.details = json.dumps(payment)
        db_payment.save()

        return HttpResponse(status=200)  # ⚠️ يجب إرجاع 200 لإعلام Mollie أن الاستلام كان ناجحًا

    except Exception as e:
        return HttpResponse(str(e), status=400)


@api_view(['GET'])
def payment_status(request, payment_id):
    try:
        payment = MolliePayment.objects.get(mollie_id=payment_id)
        return Response({
            'status': payment.status,
            'details': json.loads(payment.details)  # تحويل JSON إلى dict
        })
    except MolliePayment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=404)


@csrf_exempt
def payment_redirect(request):
    # بيانات الدفع من Mollie (تأتي كـ GET أو POST)
    payment_id = request.GET.get('id') or request.POST.get('id')
    status = request.GET.get('status') or request.POST.get('status')

    # روابط التطبيق (استبدلها بقيمك)
    app_scheme = 'yourapp://payment'  # Scheme للتطبيق
    play_store_url = 'https://play.google.com/store/apps/details?id=com.yourapp'
    app_store_url = 'https://apps.apple.com/app/id123456789'

    context = {
        'payment_id': payment_id,
        'status': status,
        'app_scheme': f"{app_scheme}?id={payment_id}&status={status}",
        'play_store_url': play_store_url,
        'app_store_url': app_store_url,
        'desktop_fallback': 'https://yourwebsite.com/thank-you'
    }

    return render(request, 'payments/redirect.html', context)
