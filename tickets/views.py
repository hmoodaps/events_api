import json
import logging

import stripe
from django.conf import settings
from django.contrib.auth.models import Group
from django.http import JsonResponse
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


# views.py
# views.py (Django)
@api_view(['POST'])
def create_mollie_payment(request):
    mollie_client = Client()
    mollie_client.set_api_key(settings.MOLLIE_API_KEY)

    # إنشاء الدفع أولاً
    payment = mollie_client.payments.create({
        'amount': {
            'currency': 'EUR',
            'value': f"{request.data['amount']:.2f}"
        },
        'description': request.data.get('description', ''),
        'redirectUrl': 'mollie://payment-return',
        'webhookUrl': request.data.get('webhookUrl', ''),
        'metadata': request.data.get('metadata', {})
    })

    # حفظ بيانات الدفع (اختياري)
    MolliePayment.objects.create(
        mollie_id=payment.id,
        amount=request.data['amount'],
        status=payment.status,
        details=json.dumps(payment)
    )

    return Response(payment)


logger = logging.getLogger(__name__)


@api_view(['GET'])
def payment_status(request):
    """
    Check the status of a Mollie payment
    Required GET parameter: payment_id
    Returns JSON with payment status and details
    """
    payment_id = request.GET.get('payment_id')

    if not payment_id:
        return Response(
            {'success': False,
             'error': 'Payment ID is required',
             'message': 'Please provide a valid payment_id parameter'},
            status=400
        )

    try:
        # Initialize Mollie client
        mollie_client = Client()
        mollie_client.set_api_key(settings.MOLLIE_API_KEY)

        # Retrieve payment from Mollie
        payment = mollie_client.payments.get(payment_id)

        response_data = {
            'success': True,
            'payment_id': payment_id,
            'status': payment.status,
            'details': {
                'amount': payment.amount,
                'description': payment.description,
                'created_at': payment.created_at,
                'method': payment.method,
            }
        }

        # Only include checkout URL if payment is still open
        if payment.status == 'open':
            response_data['checkout_url'] = payment.checkout_url

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error checking payment status for {payment_id}: {str(e)}")

        return Response(
            {
                'success': False,
                'error': 'payment_retrieval_failed',
                'payment_id': payment_id,
                'message': f"Could not retrieve payment status: {str(e)}",
                'developer_message': "Ensure the payment ID is correct and API key is valid"
            },
            status=400
        )




@api_view(['POST'])
def create_stripe_payment_intent(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Validate input values
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'eur').lower()

        if not amount:
            return Response({'error': 'Amount is required'}, status=400)

        try:
            amount = int(amount)
            if amount <= 0:
                return Response({'error': 'Amount must be greater than 0'}, status=400)
        except ValueError:
            return Response({'error': 'Amount must be a valid integer'}, status=400)

        if not isinstance(currency, str) or len(currency) != 3:
            return Response({'error': 'Currency must be a 3-letter code'}, status=400)

        # Create Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
        )

        return Response(intent)

    except stripe.error.CardError as e:
        return Response({'error': f'Card error: {e.user_message}'}, status=400)

    except stripe.error.RateLimitError:
        return Response({'error': 'Too many requests sent too quickly. Please try again later.'}, status=429)

    except stripe.error.InvalidRequestError as e:
        return Response({'error': f'Invalid request: {e.user_message}'}, status=400)

    except stripe.error.AuthenticationError:
        return Response({'error': 'Authentication with Stripe failed. Check your API key.'}, status=401)

    except stripe.error.APIConnectionError:
        return Response({'error': 'Unable to connect to Stripe. Please check your internet connection.'}, status=503)

    except stripe.error.StripeError as e:
        return Response({'error': f'General Stripe error: {e.user_message}'}, status=500)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@api_view(['GET'])
def get_stripe_payment_status(request, payment_intent_id):
    stripe.api_key = settings.STRIPE_API_KEY
    try:
        # Retrieve payment data from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return Response(intent)

    except stripe.error.InvalidRequestError:
        return Response({'error': 'Invalid Payment Intent ID'}, status=400)

    except stripe.error.AuthenticationError:
        return Response({'error': 'Authentication with Stripe failed. Check your API key.'}, status=401)

    except stripe.error.APIConnectionError:
        return Response({'error': 'Unable to connect to Stripe. Please check your internet connection.'}, status=503)

    except stripe.error.StripeError as e:
        return Response({'error': f'General Stripe error: {e.user_message}'}, status=500)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_API_KEY
    endpoint_secret = settings.STRIPE_WEBHOOK
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # 🔥 استمع فقط لـ payment_intent.succeeded
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"✅ Payment confirmed! ID: {payment_intent['id']}")

        # يمكنك هنا تحديث الطلب في قاعدة البيانات أو إرسال إشعار للمستخدم
        return JsonResponse({'status': 'Payment confirmed'})

    return JsonResponse({'status': 'Event received'})


