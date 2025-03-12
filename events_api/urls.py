"""
URL configuration for events_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('movies/', views.get_movies, name='get_movies'),
    path('stripe_keys/', views.StripeKeys.as_view(), name='stripe_keys'),  # النقطة النهاية لاسترجاع المفاتيح
    path('admin/', admin.site.urls),
    path('viewsets/', include(router.urls)),
    path('create-guest/', views.create_guest, name='create-guest'),  # النقطة النهاية لإنشاء الضيف
    path('create-superuser/', views.create_superuser, name='create-superuser'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
