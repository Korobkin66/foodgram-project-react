from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('auth/', include("djoser.urls.authtoken")),
    path('users/subscriptions/', UserViewSet.subscriptions),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
