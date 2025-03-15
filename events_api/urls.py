from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tickets import views

# تعريف الـ Router لتسجيل viewsets
router = routers.DefaultRouter()
router.register('guests', views.GuestViewSet)
router.register('movies', views.MovieViewSet)
router.register('reservations', views.ReservationViewSet)

urlpatterns = [
    # المسارات الأساسية للموقع
    path('admin/', admin.site.urls),

    # رابط لعرض مفاتيح Stripe
    path('stripe_keys/', views.StripeKeys.as_view(), name='stripe_keys'),

    # مسارات الـ viewsets الخاصة بـ guests, movies, reservations
    path('viewsets/', include(router.urls)),

    # رابط لخلق مستخدم جديد من نوع superuser
    path('create-superuser/', views.create_superuser, name='create-superuser'),

    # رابط لإنشاء ضيف جديد
    path('create-guest/', views.create_guest, name='create-guest'),

    # رابط لإنشاء حجز جديد
    path('create-reservation/', views.create_reservation, name='create-reservation'),

    # رابط لعرض الأفلام
    path('get-movies/', views.get_movies, name='get-movies'),

    # رابط لحذف الحجز باستخدام رمز الحجز
    path('delete-reservation/', views.delete_reservation, name='delete-reservation'),
path('get-reservation/', views.get_reservation_by_code, name='get-reservation'),

]

# إضافات لملفات الوسائط والصور في وضع الـ DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
