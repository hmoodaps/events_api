from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tickets import views

router = routers.DefaultRouter()
router.register('guests', views.GuestViewSet)
router.register('movies', views.MovieViewSet)
router.register('reservations', views.ReservationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stripe_keys/', views.StripeKeys.as_view(), name='stripe_keys'),
    path('viewsets/', include(router.urls)),  # هذه ستمكنك من الوصول لجميع الـ viewsets الخاصة بـ guests, movies, reservations
    path('create-guest/', views.create_guest, name='create-guest'),
    path('create-superuser/', views.create_superuser, name='create-superuser'),
    path('create-reservation/', views.create_reservation, name='create-reservation'),
    path('get-movies/', views.get_movies, name='get-movies'),  # إضافة الرابط لهذه الدالة
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
